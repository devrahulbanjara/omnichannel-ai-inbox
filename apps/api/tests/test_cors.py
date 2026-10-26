DASHBOARD = "http://localhost:3000"


def test_dashboard_origin_is_allowed(client):
    response = client.get("/health/live", headers={"Origin": DASHBOARD})

    assert response.headers["access-control-allow-origin"] == DASHBOARD
    assert "x-request-id" in response.headers["access-control-expose-headers"].lower()


def test_browser_permission_check_before_post_is_allowed(client):
    response = client.options(
        "/conversations",
        headers={
            "Origin": DASHBOARD,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == DASHBOARD


def test_unknown_origin_is_not_allowed(client):
    response = client.get("/health/live", headers={"Origin": "https://other-site.example"})

    assert "access-control-allow-origin" not in response.headers
