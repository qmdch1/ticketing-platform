package com.portfolio.ticketing.waiting;

import java.time.Instant;
import java.util.UUID;

public record WaitingToken(UUID performanceId, UUID customerId, long sequence, long rank, Instant issuedAt) {
}
