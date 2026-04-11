from chatbot.application.usecases.save_payment_step import PaymentStepOutput


def test_given_payment_step_output_when_pix_amount_accessed_then_formats_cents() -> (
    None
):
    """
    GIVEN a payment step output with pix_amount_cents
    WHEN  the computed pix_amount field is accessed
    THEN  it returns the decimal amount formatted with two digits
    """
    output = PaymentStepOutput(
        status="AWAIT_CONFIRMATION",
        pix_transaction_id="pix-123",
        pix_clipboard="000201",
        pix_qrcode="https://example.com/qr.png",
        pix_amount_cents=2345,
        step_name="payment",
    )

    assert output.pix_amount == "23.45"
