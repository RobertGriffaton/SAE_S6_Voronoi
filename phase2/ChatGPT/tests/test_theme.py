from voronoi_app.theme import get_cell_color


def test_Should_given_sameIndex_returnSameColor() -> None:
    # Arrange
    index = 7

    # Act
    first_color = get_cell_color(index)
    second_color = get_cell_color(index)

    # Assert
    assert first_color == second_color


def test_Should_given_differentIndexes_returnDifferentColors() -> None:
    # Arrange
    first_index = 1
    second_index = 2

    # Act
    first_color = get_cell_color(first_index)
    second_color = get_cell_color(second_index)

    # Assert
    assert first_color != second_color
    assert first_color.startswith("#") and len(first_color) == 7
    assert second_color.startswith("#") and len(second_color) == 7
