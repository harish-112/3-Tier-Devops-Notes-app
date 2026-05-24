import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.database import get_pool
from app.cache import get_redis, NOTES_CACHE_KEY, CACHE_TTL_SECONDS

router = APIRouter()


class NoteIn(BaseModel):
    content: str


class Note(BaseModel):
    id: str
    content: str
    created_at: str


@router.get("/", response_model=List[Note])
async def list_notes():
    redis = get_redis()

    # 1. Try cache first
    cached = await redis.get(NOTES_CACHE_KEY)
    if cached:
        return json.loads(cached)      # cache HIT — no DB call

    # 2. Cache MISS — query Postgres
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id::text, content, created_at::text FROM notes ORDER BY created_at DESC"
        )

    notes = [dict(r) for r in rows]

    # 3. Write result back to Redis for next request
    await redis.setex(NOTES_CACHE_KEY, CACHE_TTL_SECONDS, json.dumps(notes))

    return notes


@router.post("/", response_model=Note, status_code=201)
async def create_note(note: NoteIn):
    pool = await get_pool()
    redis = get_redis()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO notes (content) VALUES ($1) RETURNING id::text, content, created_at::text",
            note.content,
        )

    # Invalidate cache — next GET will rebuild from DB
    await redis.delete(NOTES_CACHE_KEY)

    return dict(row)


@router.delete("/{note_id}", status_code=204)
async def delete_note(note_id: str):
    pool = await get_pool()
    redis = get_redis()

    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM notes WHERE id = $1", note_id
        )

    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Note not found")

    await redis.delete(NOTES_CACHE_KEY)