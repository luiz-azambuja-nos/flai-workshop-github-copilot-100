"""
Tests for the High School Management System API

These tests verify the functionality of all API endpoints including
activity retrieval, student signup, and participant unregistration.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    # Store initial state
    initial_activities = {
        "Soccer Team": {
            "description": "Join the school soccer team and compete in local tournaments",
            "schedule": "Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and play friendly matches",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act, direct, and participate in school theater productions",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["liam@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Fridays, 2:00 PM - 3:30 PM",
            "max_participants": 20,
            "participants": ["elijah@mergington.edu", "charlotte@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Prepare for math competitions and solve challenging problems",
            "schedule": "Tuesdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["benjamin@mergington.edu", "amelia@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
            "max_participants": 15,
            "participants": ["ethan@mergington.edu", "grace@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Reset activities to initial state
    activities.clear()
    activities.update(initial_activities)
    yield


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_redirects_to_static(self, client):
        """Test that root redirects to static index page."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Soccer Team" in data
        assert "Basketball Club" in data
    
    def test_activities_have_required_fields(self, client):
        """Test that each activity has all required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_for_valid_activity(self, client):
        """Test successful signup for an activity."""
        response = client.post("/activities/Soccer Team/signup?email=test@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up test@mergington.edu for Soccer Team"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" in activities_data["Soccer Team"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist."""
        response = client.post("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_participant(self, client):
        """Test that a student cannot sign up twice for the same activity."""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(f"/activities/Soccer Team/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/Soccer Team/signup?email={email}")
        assert response2.status_code == 400
        data = response2.json()
        assert data["detail"] == "Student is already signed up"
    
    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple different activities."""
        email = "multi@mergington.edu"
        
        response1 = client.post(f"/activities/Soccer Team/signup?email={email}")
        assert response1.status_code == 200
        
        response2 = client.post(f"/activities/Basketball Club/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify participant is in both activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Soccer Team"]["participants"]
        assert email in activities_data["Basketball Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_existing_participant(self, client):
        """Test successful unregistration of a participant."""
        # First, sign up a student
        email = "unregister@mergington.edu"
        client.post(f"/activities/Soccer Team/signup?email={email}")
        
        # Then unregister them
        response = client.delete(f"/activities/Soccer Team/unregister?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email} from Soccer Team"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Soccer Team"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistration from an activity that doesn't exist."""
        response = client.delete("/activities/Nonexistent Activity/unregister?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_nonexistent_participant(self, client):
        """Test unregistration of a participant who isn't registered."""
        response = client.delete("/activities/Soccer Team/unregister?email=notregistered@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Participant not found"
    
    def test_unregister_initial_participant(self, client):
        """Test unregistering one of the initial participants."""
        # Lucas is initially in Soccer Team
        response = client.delete("/activities/Soccer Team/unregister?email=lucas@mergington.edu")
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "lucas@mergington.edu" not in activities_data["Soccer Team"]["participants"]
        # Mia should still be there
        assert "mia@mergington.edu" in activities_data["Soccer Team"]["participants"]


class TestActivityCapacity:
    """Tests for activity participant capacity limits."""
    
    def test_activity_has_max_participants(self, client):
        """Test that activities have a maximum participant limit defined."""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_details in activities_data.items():
            assert activity_details["max_participants"] > 0
            assert activity_details["max_participants"] >= len(activity_details["participants"])


class TestURLEncoding:
    """Tests for proper URL encoding of activity names."""
    
    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup with URL-encoded activity name."""
        # "Drama Club" with space should work when URL encoded
        response = client.post("/activities/Drama%20Club/signup?email=drama@mergington.edu")
        assert response.status_code == 200
    
    def test_unregister_with_url_encoded_activity_name(self, client):
        """Test unregister with URL-encoded activity name."""
        # First signup
        client.post("/activities/Drama%20Club/signup?email=drama@mergington.edu")
        
        # Then unregister with URL encoding
        response = client.delete("/activities/Drama%20Club/unregister?email=drama@mergington.edu")
        assert response.status_code == 200
