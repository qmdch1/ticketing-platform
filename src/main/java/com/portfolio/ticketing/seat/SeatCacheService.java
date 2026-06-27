package com.portfolio.ticketing.seat;

import java.time.Duration;
import java.util.List;
import java.util.UUID;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
public class SeatCacheService {

	private static final TypeReference<List<SeatView>> SEAT_VIEW_LIST = new TypeReference<>() {
	};

	private final StringRedisTemplate redisTemplate;
	private final ObjectMapper objectMapper;
	private final Duration ttl;

	public SeatCacheService(
			StringRedisTemplate redisTemplate,
			ObjectMapper objectMapper,
			@Value("${ticketing.seat-cache.ttl}") Duration ttl) {
		this.redisTemplate = redisTemplate;
		this.objectMapper = objectMapper;
		this.ttl = ttl;
	}

	public List<SeatView> get(UUID performanceId) {
		try {
			String payload = redisTemplate.opsForValue().get(key(performanceId));
			if (payload == null) {
				return List.of();
			}
			return objectMapper.readValue(payload, SEAT_VIEW_LIST);
		}
		catch (Exception ex) {
			evict(performanceId);
			return List.of();
		}
	}

	public void put(UUID performanceId, List<SeatView> seats) {
		try {
			redisTemplate.opsForValue().set(key(performanceId), objectMapper.writeValueAsString(seats), ttl);
		}
		catch (Exception ignored) {
			evict(performanceId);
		}
	}

	public void evict(UUID performanceId) {
		try {
			redisTemplate.delete(key(performanceId));
		}
		catch (Exception ignored) {
		}
	}

	private String key(UUID performanceId) {
		return "ticketing:seats:" + performanceId;
	}
}
