- [x] Make notifications unread count available in templates (add `unread_count` to notifications context processor)
- [x] Fix admin notification mark-read URL to `notifications:notification_mark_read`
- [ ] Enable real-time notification delivery across entire system (WebSocket and/or SSE)
- [ ] Update `rents_system/asgi.py` to route WebSocket patterns from `notifications.routing`
- [ ] Enable `ENABLE_WEBSOCKET_NOTIFICATIONS` (or add SSE fallback if WS unavailable)
- [ ] Include websocket/SSE client JS on both `accounts/templates/base_dashboard.html` and `accounts/templates/tenant/tenant_base.html`
- [ ] Bridge client updates to existing notification dropdown DOM (badge + list items)
- [ ] Run Django checks/tests and verify notification UI updates without reload

