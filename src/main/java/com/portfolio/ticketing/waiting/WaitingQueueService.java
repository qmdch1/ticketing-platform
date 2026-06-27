package com.portfolio.ticketing.waiting;

import java.time.Clock;
import java.util.UUID;

import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
public class WaitingQueueService {

	private final StringRedisTemplate redisTemplate;
	private final Clock clock;

	public WaitingQueueService(StringRedisTemplate redisTemplate, Clock clock) {
		this.redisTemplate = redisTemplate;
		this.clock = clock;
	}

	public WaitingToken issue(UUID performanceId, UUID customerId) {
		Long sequence = redisTemplate.opsForValue().increment(sequenceKey(performanceId));
		long score = sequence == null ? 1L : sequence;
		String member = customerId + ":" + score;
		redisTemplate.opsForZSet().add(queueKey(performanceId), member, score);
		Long rank = redisTemplate.opsForZSet().rank(queueKey(performanceId), member);
		return new WaitingToken(performanceId, customerId, score, rank == null ? 1L : rank + 1L, clock.instant());
	}

	private String sequenceKey(UUID performanceId) {
		return "ticketing:waiting:" + performanceId + ":sequence";
	}

	private String queueKey(UUID performanceId) {
		return "ticketing:waiting:" + performanceId + ":queue";
	}
}
