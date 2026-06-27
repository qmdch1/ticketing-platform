package com.portfolio.ticketing.waiting;

import java.time.Instant;
import java.util.UUID;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/performances/{performanceId}/waiting-room")
public class WaitingQueueController {

	private final WaitingQueueService waitingQueueService;

	public WaitingQueueController(WaitingQueueService waitingQueueService) {
		this.waitingQueueService = waitingQueueService;
	}

	@PostMapping("/tokens")
	@ResponseStatus(HttpStatus.CREATED)
	WaitingTokenResponse issue(@PathVariable UUID performanceId, @Valid @RequestBody WaitingTokenRequest request) {
		return WaitingTokenResponse.from(waitingQueueService.issue(performanceId, request.customerId()));
	}

	@DeleteMapping("/tokens/{customerId}")
	WaitingCancellationResponse cancel(@PathVariable UUID performanceId, @PathVariable UUID customerId) {
		return WaitingCancellationResponse.from(waitingQueueService.cancel(performanceId, customerId));
	}

	public record WaitingTokenRequest(@NotNull UUID customerId) {
	}

	public record WaitingTokenResponse(UUID performanceId, UUID customerId, long sequence, long rank, Instant issuedAt) {

		static WaitingTokenResponse from(WaitingToken token) {
			return new WaitingTokenResponse(
					token.performanceId(), token.customerId(), token.sequence(), token.rank(), token.issuedAt());
		}
	}

	public record WaitingCancellationResponse(
			UUID performanceId, UUID customerId, boolean cancelled, Instant cancelledAt) {

		static WaitingCancellationResponse from(WaitingCancellation cancellation) {
			return new WaitingCancellationResponse(
					cancellation.performanceId(),
					cancellation.customerId(),
					cancellation.cancelled(),
					cancellation.cancelledAt());
		}
	}
}
