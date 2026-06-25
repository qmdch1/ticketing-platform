package com.portfolio.ticketing.payment;

import java.time.Instant;
import java.util.UUID;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Size;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/orders/{orderId}/payments")
public class PaymentController {

	private final PaymentService paymentService;

	public PaymentController(PaymentService paymentService) {
		this.paymentService = paymentService;
	}

	@PostMapping
	PaymentResponse approve(
			@PathVariable UUID orderId,
			@RequestHeader("Idempotency-Key") @Size(min = 8, max = 100) String idempotencyKey,
			@Valid @RequestBody ApprovePaymentRequest request) {
		return PaymentResponse.from(paymentService.approve(orderId, idempotencyKey, request.amount()));
	}

	public record ApprovePaymentRequest(@Positive long amount) {
	}

	public record PaymentResponse(UUID id, UUID orderId, long amount, PaymentStatus status, Instant approvedAt) {
		static PaymentResponse from(Payment payment) {
			return new PaymentResponse(
					payment.getId(), payment.getOrderId(), payment.getAmount(), payment.getStatus(), payment.getApprovedAt());
		}
	}
}
