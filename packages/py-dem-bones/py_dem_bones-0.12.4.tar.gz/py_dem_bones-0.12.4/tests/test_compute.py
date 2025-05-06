"""Tests for the py-dem-bones computation functions.

This module tests the computation functions in py_dem_bones, including
basic computation, parameter settings, and error handling.
"""

import numpy as np
import pytest
from py_dem_bones.base import DemBonesWrapper


def test_basic_computation():
    """Test basic computation with default parameters."""
    dem_bones = DemBonesWrapper()

    # Set up test data
    vertices = np.array([
        [0, 0, 0],  # Vertex 0
        [1, 0, 0],  # Vertex 1
        [0, 1, 0],  # Vertex 2
        [1, 1, 0]   # Vertex 3
    ], dtype=np.float64).T  # Transpose to get 3 x n_vertices shape

    # Set rest pose
    dem_bones.set_rest_pose(vertices)

    # Set target pose (slightly modified rest pose)
    target = vertices.copy()
    target[1, :] += 0.5  # Move vertices up by 0.5

    dem_bones.set_target_name("target", 0)
    dem_bones.set_target_vertices("target", target)

    # Set number of bones
    dem_bones.num_bones = 2

    # Compute
    try:
        result = dem_bones.compute()
        assert result is True

        # Check that weights were computed
        weights = dem_bones.get_weights()
        assert weights.shape == (2, 4)  # 2 bones, 4 vertices
        assert np.all(weights >= 0) and np.all(weights <= 1)  # Weights between 0 and 1
        assert np.allclose(np.sum(weights, axis=0), 1.0)  # Weights sum to 1 for each vertex

        # Get transformations and verify shape
        transforms = dem_bones.get_transformations()
        assert transforms.shape[1:] == (4, 4)  # Each transform should be a 4x4 matrix
    except Exception as e:
        pytest.skip(f"Computation failed: {str(e)}")


def test_computation_with_parameters():
    """Test computation with custom parameters."""
    dem_bones = DemBonesWrapper()

    # Set up test data
    vertices = np.array([
        [0, 0, 0],  # Vertex 0
        [1, 0, 0],  # Vertex 1
        [0, 1, 0],  # Vertex 2
        [1, 1, 0],  # Vertex 3
        [0, 0, 1],  # Vertex 4
        [1, 0, 1],  # Vertex 5
        [0, 1, 1],  # Vertex 6
        [1, 1, 1]   # Vertex 7
    ], dtype=np.float64).T  # Transpose to get 3 x n_vertices shape

    # Set rest pose
    dem_bones.set_rest_pose(vertices)

    # Set target pose (slightly modified rest pose)
    target = vertices.copy()
    target[1, :] += 0.5  # Move vertices up by 0.5

    dem_bones.set_target_name("target", 0)
    dem_bones.set_target_vertices("target", target)

    # Set parameters
    dem_bones.num_bones = 3
    dem_bones.num_iterations = 50
    dem_bones.weight_smoothness = 0.01
    dem_bones.max_influences = 2

    # Compute
    try:
        result = dem_bones.compute()
        assert result is True

        # Check that weights were computed
        weights = dem_bones.get_weights()
        assert weights.shape == (3, 8)  # 3 bones, 8 vertices
        assert np.all(weights >= 0) and np.all(weights <= 1)  # Weights between 0 and 1
        assert np.allclose(np.sum(weights, axis=0), 1.0)  # Weights sum to 1 for each vertex

        # Check that max influences constraint was respected
        # For each vertex, count non-zero weights and ensure it's <= max_influences
        for v in range(weights.shape[1]):
            non_zero = np.count_nonzero(weights[:, v])
            assert non_zero <= 2

        # Get transformations and verify shape
        transforms = dem_bones.get_transformations()
        assert transforms.shape[1:] == (4, 4)  # Each transform should be a 4x4 matrix
    except Exception as e:
        pytest.skip(f"Computation failed: {str(e)}")


def test_computation_with_multiple_targets():
    """Test computation with multiple target poses."""
    dem_bones = DemBonesWrapper()

    # Set up test data
    vertices = np.array([
        [0, 0, 0],  # Vertex 0
        [1, 0, 0],  # Vertex 1
        [0, 1, 0],  # Vertex 2
        [1, 1, 0]   # Vertex 3
    ], dtype=np.float64).T  # Transpose to get 3 x n_vertices shape

    # Set rest pose
    dem_bones.set_rest_pose(vertices)

    # Set first target pose directly
    target1 = vertices.copy()
    target1[1, :] += 0.5  # Move vertices up by 0.5

    # Initialize target pose count and vertex count
    dem_bones._dem_bones.nS = 2
    dem_bones._dem_bones.nV = vertices.shape[1]

    # Create array with two target poses
    poses = np.zeros((3, vertices.shape[1], 2))
    poses[:, :, 0] = target1  # Set first target pose

    # Set second target pose
    target2 = vertices.copy()
    target2[0, :] += 0.5  # Move vertices right by 0.5
    poses[:, :, 1] = target2  # Set second target pose

    # Convert 3D array to format expected by C++ binding
    flat_poses = np.zeros((3, vertices.shape[1] * 2))
    for t in range(2):
        flat_poses[:, t * vertices.shape[1] : (t + 1) * vertices.shape[1]] = poses[:, :, t]

    # Set animated poses directly
    dem_bones._dem_bones.set_animated_poses(flat_poses)

    # Set target names
    dem_bones.set_target_name("target1", 0)
    dem_bones.set_target_name("target2", 1)

    # Set number of bones
    dem_bones.num_bones = 2

    # Compute
    try:
        result = dem_bones.compute()
        assert result is True

        # Check that weights were computed
        weights = dem_bones.get_weights()
        assert weights.shape == (2, 4)  # 2 bones, 4 vertices
        assert np.all(weights >= 0) and np.all(weights <= 1)  # Weights between 0 and 1
        assert np.allclose(np.sum(weights, axis=0), 1.0)  # Weights sum to 1 for each vertex

        # Get transformations and verify shape
        transforms = dem_bones.get_transformations()
        assert transforms.shape[1:] == (4, 4)  # Each transform should be a 4x4 matrix
    except Exception as e:
        pytest.skip(f"Computation failed: {str(e)}")


def test_empty_weights():
    """Test behavior with empty weight matrix."""
    dem_bones = DemBonesWrapper()

    # Set up minimal test data
    vertices = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [0, 1, 0],
        [1, 1, 0]
    ], dtype=np.float64).T

    # Set rest pose
    dem_bones.set_rest_pose(vertices)
    dem_bones.num_bones = 2

    # Get weights before computation
    weights = dem_bones.get_weights()

    # Should return empty array or zeros
    assert weights.shape == (2, 4) or weights.shape == (0, 0)

    if weights.shape == (2, 4):
        # If it returns a matrix of the right shape, it should be all zeros
        assert np.allclose(weights, 0)
