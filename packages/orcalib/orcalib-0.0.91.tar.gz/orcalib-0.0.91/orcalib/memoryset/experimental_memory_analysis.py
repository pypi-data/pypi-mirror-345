import numpy as np

from .memory_types import LabeledMemory


def similarity(x: np.ndarray, y: np.ndarray) -> float:
    """
    Compute the distance between two embeddings using the formula D(x, y) = (1 + <x, y>) / 2

    Both input embeddings are assumed to be normalized.

    Parameters:
    - x: First embedding as a NumPy array
    - y: Second embedding as a NumPy array

    Returns:
    - The distance between x and y, scaled to the range [0, 1]
    """
    dot_product = np.clip(np.dot(x, y), -1.0, 1.0)

    return (1 + dot_product) / 2


def calculate_interiority(
    embedding: np.ndarray,
    radius: float,
    memories: list[LabeledMemory],
) -> float:
    """
    EXPERIMENTAL:
    Calculate the interiority score for a given embedding within a memoryset.

    Interiority measures how deeply embedded a point is within a cluster (as defined by the radius)
    compared to other points. The score ranges from 0 to 1, where:
    - 0.0 indicates the point is not interior to the cluster
    - 1.0 indicates the point is deeply interior to the cluster

    Parameters:
    - embedding (np.ndarray): The embedding vector to calculate interiority for
    - radius (float): The maximum distance threshold to consider neighbors
    - memories: (list[LabeledMemory]): The lookup result with all memories in the memoryset

    Returns:
    - float: Interiority score between 0 and 1, where higher values indicate
              the point is more interior to the cluster
    """
    mean_memory_vector = np.zeros_like(embedding)
    local_zone = [m for m in memories if 1 - similarity(m.embedding, embedding) <= radius]

    if not local_zone:
        return 0.0  # No neighbors found, no interiority

    for m in local_zone:
        mean_memory_vector += m.embedding
    mean_memory_vector /= len(local_zone)
    # This feels weird, as I'm unclear how to interpret the score
    score = np.linalg.norm(cosine_similarity(embedding, mean_memory_vector))
    return float(score)


def calculate_isolation(
    embedding: np.ndarray,
    memories: list[LabeledMemory],
    num_neighbors: int = 20,
) -> float:
    """
    EXPERIMENTAL:
    Calculate the isolation score for a given embedding within a memoryset.
    The isolation score ranges from 0 to 1, where higher values indicate more isolation.

    Parameters:
    - embedding (np.ndarray): The embedding vector to calculate isolation for
    - memories (list[LabeledMemory]): The lookup result with all memories in the memoryset
    - num_neighbors (int, optional): Number of nearest neighbors to consider. Defaults to 5

    Returns:
    - float: Isolation score between 0 and 1, where higher values indicate more isolation

    Note:
        The function uses similarity to measure proximity between embeddings.
    """
    # Calculate similarities to all memories
    similarities = [similarity(memory.embedding, embedding) for memory in memories]
    # Sort them in ascending order
    similarities.sort(key=lambda x: x)
    # Remove the self-similarity
    if similarities[0] > 0.9999:
        similarities = similarities[1:]
    # Calculate the isolation score as 1 - the average similarity to the nearest neighbors
    return float(1 - np.mean(similarities[:num_neighbors]))


def calculate_support(
    embedding: np.ndarray,
    label: int,
    radius: float,
    memories: list[LabeledMemory],
) -> float:
    """
    EXPERIMENTAL:
    Calculate the support score for a given embedding and label within a memoryset.

    Support score represents the fraction of neighboring points within a radius that share
    the same label as the query point. The score ranges from 0 to 1, where:
    - 0.0 indicates no support (no matching labels in neighborhood)
    - 1.0 indicates full support (all neighbors share the same label)

    Parameters:
    - embedding (np.ndarray): The embedding vector to calculate support for
    - label (int): The label to compare against neighboring points
    - radius (float): The normalized maximum distance threshold to consider neighbors
    - memories (list[LabeledMemory]): The lookup result with all memories in the memoryset

    Returns:
    - float: Support score between 0 and 1, representing the fraction of
              neighboring points that share the same label

    Note:
        The function uses distance (1 - similarity) to measure
        proximity between embeddings.
    """

    radius = min(1.0, radius)  # Ensure radius is within [0, 1]
    # Calculate distances and filter points within radius
    results_within_radius = []
    for memory in memories:
        sim = similarity(memory.embedding, embedding)
        distance = 1 - sim  # Direct cosine distance
        if distance <= radius and sim < 0.9999:  # Exclude the query point itself
            results_within_radius.append(memory)

    if len(results_within_radius) == 0:
        return 0.0  # No neighbors found, no support

    # Calculate the fraction of points with matching labels
    matching_label_count = sum(1 for memory in results_within_radius if memory.label == label)
    support = matching_label_count / len(results_within_radius)
    return support


def cosine_similarity(x: np.ndarray, y: np.ndarray) -> float:
    """
    Calculate the cosine similarity between two embeddings.

    Cosine similarity is defined as the dot product of the two vectors
    divided by the product of their magnitudes.

    Parameters:
    - x: First embedding as a NumPy array
    - y: Second embedding as a NumPy array

    Returns:
    - float: Cosine similarity between x and y, ranging from -1 to 1
    """
    dot_product = np.dot(x, y)
    norm_x = np.linalg.norm(x)
    norm_y = np.linalg.norm(y)

    return float(dot_product / (norm_x * norm_y))
