import lippu.cli as cli
import lippu.api as run


def test_setup_twenty_seven():
    options = cli.parse_request([])
    cfg = run.setup_twenty_seven(options)
    assert cfg.cut is False
