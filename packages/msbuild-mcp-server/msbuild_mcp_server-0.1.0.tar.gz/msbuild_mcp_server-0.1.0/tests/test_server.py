import pytest
from server import find_msbuild, build_msbuild_project

def test_find_msbuild():
    """Test that find_msbuild returns a valid path."""
    try:
        msbuild_path = find_msbuild()
        assert msbuild_path.endswith("MSBuild.exe"), "MSBuild path does not end with MSBuild.exe"
    except FileNotFoundError:
        pytest.skip("MSBuild not found on this system.")

def test_build_msbuild_project():
    """Test the build_msbuild_project function with a mock project."""
    # Mock project path (replace with an actual test project if available)
    project_path = "mock_project.sln"
    result = build_msbuild_project(
        project_path=project_path,
        configuration="Debug",
        platform="x64",
        verbosity="minimal"
    )
    assert "Build succeeded." in result or "Build failed" in result, "Unexpected build result."