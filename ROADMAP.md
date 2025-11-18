# 🛣️ AI Ticket Classifier Roadmap (2025)

> Последнее обновление: 18 ноября 2025 г. — фактическая готовность ~90%

Этот roadmap фиксирует ключевые инициативы, которые доведут продукт до полного enterprise-grade уровня. Каждая фаза имеет измеримые deliverables и ответственных (по умолчанию — core team).

## Q1 2025 — SDK & DX
- 🧰 **SDKs**: публичные клиенты для Python (PyPI), TypeScript/Node (npm) и Go.
- 📦 **Code samples**: Postman коллекция, примеры интеграции с auth.
- 🧪 **DX tooling**: генерация клиентов из OpenAPI, инструкции по тестовым окружениям.

## Q2 2025 — Webhooks, Data, TLS
- 🔔 **Webhooks v2**: retry-политики, HMAC-подпись, self-serve управление.
- 🗄️ **PostgreSQL persistence**: хранение API ключей/usage, миграции Alembic.
- 🔐 **TLS/Ingress**: Traefik/Nginx чарты, автоматические сертификаты (Let's Encrypt).
- 📘 **Kubernetes manifests**: helm chart + GitOps пример.

## Q3 2025 — Billing & Admin UI
- 💳 **Billing**: usage-based тарификация, отчёты, экспорт счетов (CSV/Stripe).
- 🖥️ **Admin UI**: управление ключами, тарифами, мониторинг ошибок/latency.
- 📈 **SLA/SLO dashboard**: визуализация фактических метрик vs целей.

## Q4 2025 — Enterprise SSO & Alerting
- 🧑‍💼 **SSO**: поддержка SAML/OIDC, роли и пермишены.
- 🚨 **Advanced alerting**: Prometheus Alertmanager → PagerDuty/Slack, runbooks.
- ♻️ **DR/BCP**: автоматические бэкапы, восстановление, chaos/fire-drills.
- 📑 **Compliance pack**: SOC2-ready чек-листы, DPA шаблоны, security review.

## SLO / SLA Targets
| Метрика                | Цель            | Комментарий |
|------------------------|-----------------|-------------|
| Availability           | ≥ 99.5%         | Multi-region deploy + health checks |
| p95 latency /classify  | ≤ 700 ms        | Retry + caching prompts |
| Accuracy (F1)          | ≥ 0.85          | Регулярные eval runs |
| Incident response time | ≤ 15 минут      | On-call + PagerDuty |

## Как участвовать
1. Создавать issues/PR с метками `roadmap/qX` и описанием deliverables.
2. После завершения пункта обновлять README/PRODUCTION_READINESS_REPORT.
3. Отражать прогресс в релизных заметках и прод-чеклисте.
