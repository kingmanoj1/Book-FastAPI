import pytest
from httpx import AsyncClient
from main import app, create_token, init_db
import sqlite3

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # Reset database before tests
    init_db()
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM my_books")
    conn.commit()
    conn.close()

@pytest.fixture
def token():
    return create_token()

@pytest.mark.asyncio
async def test_token_generation():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/token")
    assert response.status_code == 200
    assert "token" in response.json()

@pytest.mark.asyncio
async def test_create_book_success(token):
    headers = {"Authorization": f"Bearer {token}"}
    book_data = {
        "name": "Test Book",
        "description": "A test book",
        "pages": 100,
        "author": "Author A",
        "publisher": "Publisher A"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/books", json=book_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Book created"

@pytest.mark.asyncio
async def test_create_book_missing_field(token):
    headers = {"Authorization": f"Bearer {token}"}
    book_data = {
        "name": "Incomplete Book",
        "description": "Missing fields",
        "pages": 50,
        "author": "Author B"
        # Missing 'publisher'
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/books", json=book_data, headers=headers)
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_create_book_unauthorized():
    book_data = {
        "name": "Unauthorized Book",
        "description": "No token",
        "pages": 200,
        "author": "Author C",
        "publisher": "Publisher C"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/books", json=book_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_books_pagination(token):
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/books?page_no=1", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_books_with_filters(token):
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/books?author=Author A&publisher=Publisher A", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(book["author"] == "Author A" for book in data)

@pytest.mark.asyncio
async def test_get_books_invalid_page(token):
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/books?page_no=0", headers=headers)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_delete_book_success(token):
    headers = {"Authorization": f"Bearer {token}"}

    # Insert a test book to delete
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO my_books (name, description, pages, author, publisher) VALUES (?, ?, ?, ?, ?)",
                   ("To Delete", "Description", 123, "Del Author", "Del Pub"))
    book_id = cursor.lastrowid
    conn.commit()
    conn.close()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(f"/books/{book_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Book deleted"

@pytest.mark.asyncio
async def test_delete_book_invalid_id(token):
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/books/999999", headers=headers)
    assert response.status_code == 200  # Still returns 200 even if nothing is deleted
    assert response.json()["message"] == "Book deleted"

@pytest.mark.asyncio
async def test_invalid_token():
    headers = {"Authorization": "Bearer invalid.token.value"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/books", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"
