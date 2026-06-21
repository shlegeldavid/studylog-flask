def test_404_page_is_shown_in_russian(client):
    response = client.get("/missing-page")
    page = response.get_data(as_text=True)

    assert response.status_code == 404
    assert "Страница не найдена" in page
    assert "Вернуться на главную" in page
