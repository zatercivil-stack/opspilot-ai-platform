# Решение может быть принято только один раз

Источник: `src/lib/approvals.ts`, версия `9b13cd7`, функция `decideApproval`. Выдержка находится внутри транзакции; проверка полномочий выполняется на границе API. Фрагмент не содержит остальных эффектов решения и не является полным обработчиком.

```typescript
    // Атомарное обновление только для ожидающего решения
    const res = await tx.update(approvals)
      .set({ status: decision, decidedBy: user.email, comment: body.comment, decidedAt: now })
      .where(and(eq(approvals.id, id), eq(approvals.status, "pending")))
      .returning();
    if (res.length === 0) {
      const [ap] = await tx.select().from(approvals).where(eq(approvals.id, id)).limit(1);
      if (!ap) throw new ApiError(404, "Согласование не найдено");
      throw new ApiError(409, "Решение по этому согласованию уже принято");
    }
```

Условие `status = pending` проверяется самим PostgreSQL при изменении строки. Если другой запрос уже принял решение, обновление не возвращает запись и вызывающий получает конфликт. В полной функции изменение связанной сущности и аудит используют ту же транзакцию. Один только этот фрагмент не доказывает корректность всего процесса — для этого нужна интеграционная проверка.

Лицензия: [MIT, Copyright (c) 2026 OpsPilot AI](../licenses/MIT-legacy.txt).
