"""HTTP controller for payment provider notifications."""

from fastapi import APIRouter, HTTPException, status

from src.adapters.schemas.sale import PaymentWebhookRequest, SaleResponse
from src.application.exceptions.sale_exceptions import (
    PaymentAlreadyProcessedError,
    SaleNotFoundError,
)
from src.application.use_case.process_payment import ProcessPaymentUseCase


def create_payment_router(process_payment_use_case: ProcessPaymentUseCase) -> APIRouter:
    """Build the payment webhook route with an injected use case."""

    router = APIRouter(prefix="/payments", tags=["payments"])

    @router.post("/webhook")
    def payment_webhook(payload: PaymentWebhookRequest) -> SaleResponse:
        try:
            sale = process_payment_use_case.execute(payload.payment_code, payload.status)
        except SaleNotFoundError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found") from error
        except PaymentAlreadyProcessedError as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Payment was already processed with a different status.",
            ) from error
        return SaleResponse.model_validate(sale)

    return router
