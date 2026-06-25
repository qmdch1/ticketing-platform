package com.portfolio.ticketing.order;

import java.util.UUID;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1")
public class OrderController {

	private final OrderService orderService;

	public OrderController(OrderService orderService) {
		this.orderService = orderService;
	}

	@PostMapping("/reservations/{reservationId}/orders")
	@ResponseStatus(HttpStatus.CREATED)
	OrderResponse create(@PathVariable UUID reservationId, @Valid @RequestBody CreateOrderRequest request) {
		return OrderResponse.from(orderService.create(reservationId, request.customerId()));
	}

	public record CreateOrderRequest(@NotNull UUID customerId) {
	}

	public record OrderResponse(UUID id, UUID reservationId, long totalAmount, OrderStatus status) {
		static OrderResponse from(TicketOrder order) {
			return new OrderResponse(order.getId(), order.getReservationId(), order.getTotalAmount(), order.getStatus());
		}
	}
}
