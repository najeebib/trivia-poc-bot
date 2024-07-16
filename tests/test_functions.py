from main import handle_response

def test_handle_response_invalid_category():
    question, correct_answer = handle_response("99")
    assert question is None
    assert correct_answer is None

def test_handle_response_valid_category():
    question, correct_answer = handle_response("20")
    assert question is not None
    assert correct_answer is not None

