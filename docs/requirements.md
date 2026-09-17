# TicketCore Requirements

## 1. Problem Statement

TicketCore is a backend system for an event ticketing platform where
users can discover events, temporarily reserve seats, complete payments,
and receive confirmed ticket orders.

The system is designed to handle high-demand ticket sales where many
users may attempt to reserve the same limited inventory concurrently.

The system must prevent double booking, maintain consistent booking and
payment state, handle failures safely, and support horizontal scaling.

## 2. Actors

### Customer

A customer can:

- Register and log in
- Browse available events
- View event details
- View available seats
- Temporarily reserve one or more seats
- Complete checkout
- View reservation status
- View previous orders
- Cancel a reservation when allowed

### Administrator

An administrator can:

- Create venues
- Create events
- Configure seats and prices
- Publish/cancel events
- View reservations
- View orders

## 3. Booking Flow

1. Administrator creates a venue.
2. Administrator creates an event at the venue.
3. Seats and prices are configured for the event.
4. Customer browses available events.
5. Customer selects an event.
6. Customer views available seats.
7. Customer selects one or more seats.
8. TicketCore attempts to reserve the selected seats.
9. If the seats are available, TicketCore creates a temporary reservation.
10. The reservation expires after a limited amount of time.
11. Customer completes payment before expiration.
12. Successful payment confirms the reservation.
13. Reserved seats become sold.
14. TicketCore creates an order.
15. Ticket/ticket-confirmation processing happens asynchronously.

## 4. Core Entities

The initial system contains:

- User
- Venue
- Event
- Seat
- Reservation
- ReservationSeat
- Payment
- Order
- OrderItem

## 5. Business Rules

1. A seat cannot be actively reserved by multiple customers at the same time.

2. A sold seat cannot be reserved again.

3. Reservations are temporary and have an expiration time.

4. When a reservation expires, its seats become available again.

5. Payment can only be attempted for a valid, non-expired reservation.

6. A reservation becomes confirmed only after successful payment.

7. A successful order must reference the reservation and payment that created it.

8. Duplicate checkout requests must not create duplicate payments or orders.

9. Customers can only access their own reservations and orders.

10. Administrative operations require administrator privileges.

## 6. Important System Scenarios

These scenarios define critical situations that TicketFlow must handle
correctly, especially under concurrency, retries, and system failures.

---

### Scenario 1: Concurrent Seat Reservation

#### Situation

Multiple users attempt to reserve the same EventSeat at approximately
the same time.

Example:

User A → Coldplay + Seat A12
User B → Coldplay + Seat A12
User C → Coldplay + Seat A12

#### Expected Behavior

- Exactly one reservation should successfully acquire the EventSeat.
- All other reservation attempts should fail with a conflict.
- The EventSeat must never have multiple active reservations.

#### Invariant

One EventSeat can have at most one active reservation at a time.

### Scenario 2: Reservation Expiration

#### Situation

A user successfully reserves an EventSeat but does not complete
checkout before the reservation expires.

Example:

10:00 AM → Seat A12 is reserved
10:05 AM → Reservation expires

#### Expected Behavior

- Reservation status changes to EXPIRED.
- The EventSeat becomes available again.
- Another customer can reserve the EventSeat.

#### Invariant

An expired reservation must never continue blocking an EventSeat.

---
### Scenario 3: Duplicate Checkout Request

#### Situation

A customer submits checkout but experiences a network timeout and
retries the same request.

Example:

POST /reservations/123/checkout
Idempotency-Key: abc123

The same request is submitted multiple times.

#### Expected Behavior

- TicketCore processes the checkout operation only once.
- Only one successful payment should be associated with the purchase.
- Only one order should be created.
- Repeated requests should return the result of the original operation.

#### Invariant

Retrying the same checkout operation must not create duplicate
side effects.

---
### Scenario 4: Payment Failure

#### Situation

A customer has an active reservation but the payment attempt fails.

#### Expected Behavior

- Payment status becomes FAILED.
- Reservation must not become CONFIRMED.
- EventSeats must not become SOLD.
- No confirmed order should be created.
- The customer may retry payment while the reservation remains valid.

#### Invariant

An EventSeat can become SOLD only after successful payment.

---

### Scenario 5: Payment Succeeds but Application Crashes

#### Situation

The external payment provider successfully processes a payment, but
the TicketCore application crashes before completing all local state
updates.

Example:

Payment Provider → SUCCESS
          ↓
TicketFlow crashes

#### Expected Behavior

The system must eventually recover the successful payment and bring
the reservation, order, and EventSeat states into a consistent state.

#### Invariant

A successfully processed payment must not be permanently lost because
of an application failure.

## 7. Functional Requirements

### Authentication
- Users can register.
- Users can log in.
- The system supports CUSTOMER and ADMIN roles.

### Events
- Administrators can create events.
- Customers can browse active events.
- Customers can retrieve event details.

### Seats
- Events contain bookable seats.
- Customers can view seat availability.
- Administrators can configure seat pricing.

### Reservations
- Customers can reserve one or more available seats.
- Reservations expire after a configured duration.
- Expired reservations release their seats.
- Double booking must be prevented.

### Payments
- Customers can checkout an active reservation.
- Payment success confirms the reservation.
- Payment failure must not create a confirmed order.
- Checkout must support idempotency.

### Orders
- Successful checkout creates an order.
- Customers can retrieve their orders.

## 8. Non-Functional Requirements

### Correctness
The system must never sell the same seat twice.

### Consistency
Reservation, seat, payment, and order states must remain consistent.

### Concurrency
The system must safely handle multiple customers attempting to reserve
the same seat simultaneously.

### Scalability
API servers should remain stateless where possible so multiple instances
can run behind a load balancer.

### Reliability
Failures in background processing must support retries and recovery.

### Idempotency
Retrying critical operations must not create duplicate side effects.

### Performance
Frequently accessed, slowly changing data should be cacheable.

### Security
Protected resources require authentication and authorization.

### Observability
The system should eventually expose structured logs, metrics, and
request correlation IDs.