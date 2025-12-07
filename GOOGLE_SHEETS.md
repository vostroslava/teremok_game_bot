# Google Sheets Integration (via Webhook)

## Быстрая настройка

Мы используем Google Apps Script как вебхук. Скрипт теперь поддерживает **умную дедупликацию** (обновляет существующие записи по User ID) и **пакетную загрузку**.

### 1. Подготовка таблицы

1. Создайте Google Таблицу.
2. Перейдите в **Расширения** (Extensions) -> **Apps Script**.
3. Вставьте этот код в `Code.gs` (полностью замените старый):

```javascript
function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.tryLock(10000); // Wait up to 10s for previous request to finish
  
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const rawData = JSON.parse(e.postData.contents);
    
    // Support both single object and array of objects
    const dataList = Array.isArray(rawData) ? rawData : [rawData];
    if (dataList.length === 0) return ContentService.createTextOutput(JSON.stringify({status: 'ok', count: 0}));
    
    // Determine sheet based on first item (assuming batch assumes same type)
    const type = dataList[0].type;
    const sheetName = type === 'test' ? 'Тесты' : 'Лиды';
    let sheet = ss.getSheetByName(sheetName);
    
    // Create sheet if missing
    if (!sheet) {
      sheet = ss.insertSheet(sheetName);
      if (type === 'test') {
        sheet.appendRow(['Дата', 'Имя', 'Роль', 'Компания', 'Телефон', 'Результат', 'Баллы', 'Продукт', 'User ID']);
      } else {
        sheet.appendRow(['Дата', 'Имя', 'Роль', 'Компания', 'Телефон', 'Telegram', 'Статус', 'Размер команды', 'User ID']);
      }
    }
    
    // --- SMART UPSERT LOGIC ---
    
    // 1. Get all existing User IDs to map them to row numbers
    // User ID is in the last column (column 9)
    const lastRow = sheet.getLastRow();
    const idMap = new Map(); // UserId -> RowIndex
    
    if (lastRow > 1) {
      const idValues = sheet.getRange(2, 9, lastRow - 1, 1).getValues();
      for (let i = 0; i < idValues.length; i++) {
        const id = String(idValues[i][0]);
        if (id) idMap.set(id, i + 2); // +2 because 0-index + 1 header + 1 for 1-based index
      }
    }
    
    // 2. Process incoming data
    const rowsToAdd = [];
    
    dataList.forEach(data => {
      let row = [];
      const userId = String(data.user_id || '');
      const timestamp = new Date();
      
      if (type === 'test') {
        row = [
          timestamp,
          data.name || '',
          data.role || '',
          data.company || '',
          data.phone || '',
          data.result_type || '',
          data.scores || '',
          data.product || 'teremok',
          userId
        ];
      } else {
        row = [
          timestamp,
          data.name || '',
          data.role || '',
          data.company || '',
          data.phone || '',
          data.telegram || '',
          data.status || 'new',
          data.team_size || '',
          userId
        ];
      }
      
      // Upsert: Update if exists, else prepare to add
      if (userId && idMap.has(userId)) {
        const textRowIndex = idMap.get(userId);
        sheet.getRange(textRowIndex, 1, 1, row.length).setValues([row]);
      } else {
        rowsToAdd.push(row);
      }
    });
    
    // 3. Batch append new rows
    if (rowsToAdd.length > 0) {
      sheet.getRange(lastRow + 1, 1, rowsToAdd.length, rowsToAdd[0].length).setValues(rowsToAdd);
    }
    
    return ContentService.createTextOutput(JSON.stringify({status: 'ok', updated: dataList.length, added: rowsToAdd.length}));
    
  } catch (e) {
    return ContentService.createTextOutput(JSON.stringify({status: 'error', message: e.toString()}));
  } finally {
    lock.releaseLock();
  }
}
```

### 2. Публикация (Deploy)

1. **Начать развертывание** -> **Управление развертываниями**.
2. **Отредактировать** (карандаш) текущее развертывание.
3. **Версия**: *Новая версия* (обязательно выберите это!).
4. **Начать развертывание**.
5. URL не изменится, но код обновится.

---

## Что изменилось?
- Теперь скрипт проверяет **User ID** (колонка I).
- Если ID уже есть в таблице, он **обновит** строку (например, статус лида или новый результат теста).
- Если ID нет, добавит новую строку.
- Работает намного быстрее при массовой выгрузке.
