package com.portfolio.ticketing.reservation;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

import com.portfolio.ticketing.TestcontainersConfiguration;
import com.portfolio.ticketing.common.BusinessException;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;

@Import(TestcontainersConfiguration.class)
@SpringBootTest
class ReservationConcurrencyTest {

	private static final UUID PERFORMANCE_ID = UUID.fromString("11111111-1111-1111-1111-111111111111");
	private static final UUID SEAT_ID = UUID.fromString("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1");
	private static final int REQUEST_COUNT = 20;

	@Autowired
	private ReservationService reservationService;

	@Test
	void allowsOnlyOneReservationWhenCustomersRequestTheSameSeatConcurrently() throws Exception {
		CountDownLatch ready = new CountDownLatch(REQUEST_COUNT);
		CountDownLatch start = new CountDownLatch(1);
		List<Future<Boolean>> results = new ArrayList<>();

		try (var executor = Executors.newFixedThreadPool(REQUEST_COUNT)) {
			for (int i = 0; i < REQUEST_COUNT; i++) {
				results.add(executor.submit(() -> {
					ready.countDown();
					start.await();
					try {
						reservationService.hold(PERFORMANCE_ID, UUID.randomUUID(), List.of(SEAT_ID));
						return true;
					}
					catch (BusinessException exception) {
						assertThat(exception.code()).isEqualTo("SEAT_NOT_AVAILABLE");
						return false;
					}
				}));
			}

			ready.await();
			start.countDown();
		}

		long successCount = 0;
		for (Future<Boolean> result : results) {
			if (result.get()) {
				successCount++;
			}
		}

		assertThat(successCount).isEqualTo(1);
		assertThat(results).hasSize(REQUEST_COUNT);
	}
}
