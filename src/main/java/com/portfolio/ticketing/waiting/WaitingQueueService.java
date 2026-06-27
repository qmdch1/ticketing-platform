package com.portfolio.ticketing.waiting;

import java.time.Clock;
import java.util.UUID;

import com.portfolio.ticketing.common.BusinessException;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.http.HttpStatus;
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
		String existingMember = member(performanceId, customerId);
		if (existingMember != null) {
			return token(performanceId, customerId, existingMember);
		}

		Long sequence = redisTemplate.opsForValue().increment(sequenceKey(performanceId));
		long score = sequence == null ? 1L : sequence;
		String member = customerId + ":" + score;
		redisTemplate.opsForZSet().add(queueKey(performanceId), member, score);
		redisTemplate.opsForHash().put(memberKey(performanceId), customerId.toString(), member);
		return token(performanceId, customerId, member);
	}

	public WaitingCancellation cancel(UUID performanceId, UUID customerId) {
		String member = member(performanceId, customerId);
		if (member == null) {
			throw new BusinessException(
					HttpStatus.NOT_FOUND, "WAITING_TOKEN_NOT_FOUND", "Waiting token does not exist");
		}
		redisTemplate.opsForZSet().remove(queueKey(performanceId), member);
		redisTemplate.opsForHash().delete(memberKey(performanceId), customerId.toString());
		return new WaitingCancellation(performanceId, customerId, true, clock.instant());
	}

	private WaitingToken token(UUID performanceId, UUID customerId, String member) {
		long sequence = sequence(member);
		Long rank = redisTemplate.opsForZSet().rank(queueKey(performanceId), member);
		return new WaitingToken(performanceId, customerId, sequence, rank == null ? 1L : rank + 1L, clock.instant());
	}

	private String member(UUID performanceId, UUID customerId) {
		Object member = redisTemplate.opsForHash().get(memberKey(performanceId), customerId.toString());
		return member instanceof String value ? value : null;
	}

	private long sequence(String member) {
		int separator = member.lastIndexOf(':');
		if (separator < 0 || separator == member.length() - 1) {
			throw new BusinessException(HttpStatus.CONFLICT, "INVALID_WAITING_TOKEN", "Waiting token is corrupted");
		}
		return Long.parseLong(member.substring(separator + 1));
	}

	private String sequenceKey(UUID performanceId) {
		return "ticketing:waiting:" + performanceId + ":sequence";
	}

	private String queueKey(UUID performanceId) {
		return "ticketing:waiting:" + performanceId + ":queue";
	}

	private String memberKey(UUID performanceId) {
		return "ticketing:waiting:" + performanceId + ":members";
	}
}
