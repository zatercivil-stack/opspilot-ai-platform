# Проверка двух одновременных решений

Источник: `tests/integration/flows.test.ts`, версия `9b13cd7`. Выдержка одного интеграционного теста. Фикстуры, соединение с БД и прикладной код здесь не поставляются; проверка выполняется в отдельной тестовой PostgreSQL, не в production.

```typescript
  it("commits exactly one of two simultaneous decisions", async () => {
    const { actor, item, ap } = await approval();
    const results = await Promise.allSettled([true, false].map(approve => decideApproval(actor, ap.id, { approve, comment: "" })));
    expect(results.filter(result => result.status === "fulfilled")).toHaveLength(1);
    const [saved] = await db.select().from(approvals).where(eq(approvals.id, ap.id));
    const [request] = await db.select().from(requests).where(eq(requests.id, item.id));
    expect(request.status).toBe(saved.status === "approved" ? "resolved" : "in_progress");
  });
```

Тест одновременно отправляет противоположные решения. Проверяет единственный успешный исход и соответствие статуса обращения принятому решению. Отдельный тест полной реализации проверяет откат при ошибке аудита. Один прогон конкуренции не является доказательством отсутствия всех гонок; полезны повторения с разными порядками запросов и нагрузочные проверки.

Лицензия: [MIT, Copyright (c) 2026 OpsPilot AI](../licenses/MIT-legacy.txt).
