"""Test main."""


def test_main(mocker):
    mock_print = mocker.patch("builtins.print")

    assert mock_print.called_once_with("Hello World!")
