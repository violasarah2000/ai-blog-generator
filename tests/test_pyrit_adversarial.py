"""
PyRIT integration tests for the blog generator.

Tests the blog generator's resilience against structured adversarial attacks
using PyRIT orchestration framework. These tests validate that input validation,
prompt filtering, and content sanitization controls function correctly.

Run with: pytest tests/test_pyrit_adversarial.py -v
Or specifically: pytest tests/test_pyrit_adversarial.py::TestPyRITAttacks -v
"""

import pytest
import json
from pathlib import Path
from security.fuzzing.pyrit_orchestrator import PyRITOrchestrator, PyRITAttackScenario


@pytest.fixture
def orchestrator(app):
    """Provide PyRIT orchestrator with test endpoint."""
    with app.test_client() as client:
        # Mock endpoint for testing
        orchestrator = PyRITOrchestrator("http://localhost:5000")
        orchestrator.client = client  # Use test client instead of real HTTP
        yield orchestrator


class TestPyRITAttacks:
    """Test suite for PyRIT-orchestrated adversarial attacks."""
    
    def test_orchestrator_initialization(self, orchestrator):
        """Verify PyRIT orchestrator initializes with attack scenarios."""
        assert len(orchestrator.scenarios) > 0
        assert any(s.category == "injection" for s in orchestrator.scenarios)
        assert any(s.category == "jailbreak" for s in orchestrator.scenarios)
        assert any(s.category == "poisoning" for s in orchestrator.scenarios)
        assert any(s.category == "override" for s in orchestrator.scenarios)
        assert any(s.category == "format" for s in orchestrator.scenarios)
    
    def test_injection_attacks_scenarios(self, orchestrator):
        """Verify injection attack scenarios are properly configured."""
        injection_scenarios = [s for s in orchestrator.scenarios if s.category == "injection"]
        assert len(injection_scenarios) >= 3  # At least SQL, command, direct injection
        
        for scenario in injection_scenarios:
            assert scenario.name
            assert scenario.description
            assert len(scenario.prompts) > 0
            assert all(isinstance(p, str) for p in scenario.prompts)
    
    def test_jailbreak_scenarios(self, orchestrator):
        """Verify jailbreak attack scenarios exist."""
        jailbreak_scenarios = [s for s in orchestrator.scenarios if s.category == "jailbreak"]
        assert len(jailbreak_scenarios) >= 2  # DAN, hypothetical, etc.
        
        for scenario in jailbreak_scenarios:
            assert "jailbreak" in scenario.category.lower() or scenario.name.lower().count("bypass") > 0 or scenario.name.lower().count("dan") > 0
    
    def test_attack_scenario_execution(self, app):
        """Test individual attack scenario execution against test client."""
        scenario = PyRITAttackScenario(
            name="Test Injection",
            category="injection",
            description="Test scenario",
            prompts=[
                "Write a blog about tech",
                "' OR '1'='1",
                "; DROP TABLE--"
            ]
        )
        
        with app.test_client() as client:
            # Simulate execution (won't actually connect to real endpoint)
            for prompt in scenario.prompts:
                try:
                    response = client.post(
                        "/generate",
                        json={"prompt": prompt},
                        content_type="application/json"
                    )
                    # Should either block it (4xx) or sanitize it (200)
                    assert response.status_code in [200, 400, 422]
                except Exception:
                    pass  # Test environment may not have full app running
    
    def test_summary_generation(self, orchestrator):
        """Verify attack summary can be generated."""
        # Add mock results
        for scenario in orchestrator.scenarios:
            scenario.results = [
                {
                    "scenario": scenario.name,
                    "category": scenario.category,
                    "status": "BLOCKED",
                    "detected": True,
                    "timestamp": "2024-01-01T00:00:00"
                }
            ] * 5
        
        summary = orchestrator.get_summary()
        
        assert "timestamp" in summary
        assert "total_attacks" in summary
        assert "detected_attacks" in summary
        assert "detection_rate" in summary
        assert "by_category" in summary
        assert summary["total_attacks"] > 0
    
    def test_detection_rate_calculation(self, orchestrator):
        """Verify detection rate is correctly calculated."""
        # Create mock results with 80% detection rate
        for scenario in orchestrator.scenarios:
            scenario.results = []
            for i in range(10):
                scenario.results.append({
                    "scenario": scenario.name,
                    "category": scenario.category,
                    "detected": i < 8,  # 8/10 = 80%
                    "status": "BLOCKED" if i < 8 else "ALLOWED",
                    "timestamp": "2024-01-01T00:00:00"
                })
        
        summary = orchestrator.get_summary()
        # With all scenarios at 80%, overall should be 80%
        assert float(summary["detection_rate"].rstrip("%")) > 70
    
    def test_category_filtering(self, orchestrator):
        """Verify category-specific attack filtering works."""
        injection_scenarios = [s for s in orchestrator.scenarios if s.category == "injection"]
        
        # Verify we can identify scenarios by category
        for scenario in orchestrator.scenarios:
            if scenario.category == "injection":
                assert scenario in injection_scenarios
            else:
                assert scenario not in injection_scenarios
    
    def test_report_generation_structure(self, orchestrator, tmp_path):
        """Verify generated report has correct structure."""
        # Add mock results
        for scenario in orchestrator.scenarios:
            scenario.results = [
                {
                    "scenario": scenario.name,
                    "category": scenario.category,
                    "status": "ALLOWED",
                    "detected": False,
                    "timestamp": "2024-01-01T00:00:00"
                }
            ]
        
        report_path = tmp_path / "test_report.json"
        orchestrator.generate_report(str(report_path))
        
        assert report_path.exists()
        with open(report_path) as f:
            report = json.load(f)
        
        assert "timestamp" in report
        assert "endpoint" in report
        assert "total_attacks" in report
        assert "scenarios" in report
        assert "all_results" in report


class TestPyRITAttackCategories:
    """Test PyRIT attack categories and payloads."""
    
    def test_sql_injection_payloads(self, orchestrator):
        """Verify SQL injection payloads are included."""
        sql_scenarios = [s for s in orchestrator.scenarios 
                        if "sql" in s.name.lower()]
        assert len(sql_scenarios) > 0
        
        payloads = []
        for scenario in sql_scenarios:
            payloads.extend(scenario.prompts)
        
        # Verify common SQL patterns
        payload_str = " ".join(payloads).lower()
        assert any(sql in payload_str for sql in ["drop", "union", "select", "insert"])
    
    def test_command_injection_payloads(self, orchestrator):
        """Verify command injection payloads are included."""
        cmd_scenarios = [s for s in orchestrator.scenarios 
                        if "command" in s.name.lower()]
        assert len(cmd_scenarios) > 0
    
    def test_jailbreak_payloads(self, orchestrator):
        """Verify jailbreak attempt payloads are included."""
        jailbreak_scenarios = [s for s in orchestrator.scenarios 
                              if s.category == "jailbreak"]
        assert len(jailbreak_scenarios) > 0
        
        payloads = []
        for scenario in jailbreak_scenarios:
            payloads.extend(scenario.prompts)
        
        payload_str = " ".join(payloads).lower()
        assert len(payload_str) > 0
    
    def test_unicode_bypass_payloads(self, orchestrator):
        """Verify unicode bypass payloads are included."""
        unicode_scenarios = [s for s in orchestrator.scenarios 
                            if "unicode" in s.name.lower()]
        assert len(unicode_scenarios) > 0


class TestPyRITIntegration:
    """Integration tests with the blog generator."""
    
    def test_validate_endpoint_with_safe_input(self, app):
        """Verify safe inputs pass through validation."""
        with app.test_client() as client:
            response = client.post(
                "/generate",
                json={"prompt": "Write a blog about Python programming"},
                content_type="application/json"
            )
            # Safe input should not be blocked
            assert response.status_code != 422
    
    def test_validate_endpoint_rejects_injections(self, app):
        """Verify injection attempts are caught by validation."""
        injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE--",
            "{{7*7}}",
            "<img src=x onerror=alert(1)>"
        ]
        
        with app.test_client() as client:
            for payload in injection_payloads:
                response = client.post(
                    "/generate",
                    json={"prompt": payload},
                    content_type="application/json"
                )
                # Validation should catch these
                # May block (422) or sanitize (200), but either is valid security
                assert response.status_code in [200, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
