import modules.new_db_logic as logic


def test_check_user():
    assert logic.check_user('"ffd"') == 1
