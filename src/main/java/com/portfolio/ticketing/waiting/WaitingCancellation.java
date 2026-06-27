package com.portfolio.ticketing.waiting;

import java.time.Instant;
import java.util.UUID;

public record WaitingCancellation(UUID performanceId, UUID customerId, boolean cancelled, Instant cancelledAt) {
}
