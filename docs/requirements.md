# TicketFlow Requirements

## 1. Problem Statement

TicketFlow is a backend system for an event ticketing platform where
users can discover events, temporarily reserve seats, complete payments,
and receive confirmed ticket orders.

The system is designed to handle high-demand ticket sales where many
users may attempt to reserve the same limited inventory concurrently.

The system must prevent double booking, maintain consistent booking and
payment state, handle failures safely, and support horizontal scaling.