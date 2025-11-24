document.addEventListener('DOMContentLoaded', function () {
    const formsetContainer = document.getElementById('formset-container');
    const addButton = document.getElementById('add-question-btn');
    const emptyFormTemplate = document.getElementById('empty-form-template');

    // Находим скрытый input, отвечающий за количество форм
    // Ищем максимально агрессивно
    const totalFormsInput = document.querySelector('input[name$="TOTAL_FORMS"]');

    if (!totalFormsInput) {
        alert("ОШИБКА: Django не отдал input TOTAL_FORMS. Проверь view.py!");
        return;
    }

    addButton.addEventListener('click', function () {
        // 1. Считаем текущее количество
        let currentFormCount = parseInt(totalFormsInput.value);
        
        // 2. Берем HTML из шаблона
        let newHtml = emptyFormTemplate.innerHTML;

        // 3. ЗАМЕНА (Самое важное): меняем __prefix__ на число
        // Используем глобальную замену
        newHtml = newHtml.replace(/__prefix__/g, currentFormCount);
        // Меняем визуальный номер __num__
        newHtml = newHtml.replace(/__num__/g, currentFormCount + 1);

        // 4. Вставляем в страницу
        formsetContainer.insertAdjacentHTML('beforeend', newHtml);

        // 5. НАСИЛЬНОЕ ВКЛЮЧЕНИЕ ПОЛЕЙ (Фикс твоей проблемы)
        // Берем только что добавленный блок
        const newBlock = formsetContainer.lastElementChild;
        
        // Находим все инпуты в этом блоке
        const inputs = newBlock.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            // Снимаем любые блокировки
            input.removeAttribute('disabled');
            input.removeAttribute('readonly');
            input.disabled = false;
            
            // Насильно ставим белый фон и разрешаем клики
            input.style.backgroundColor = '#ffffff';
            input.style.pointerEvents = 'auto';
            input.style.opacity = '1';
        });

        // 6. Обновляем счетчик Django
        const nextCount = currentFormCount + 1;
        // Обновляем ВСЕ счетчики (и questions, и answers если есть)
        document.querySelectorAll('input[name$="TOTAL_FORMS"]').forEach(input => {
            input.value = nextCount;
        });

    });

    // Обработка удаления (крестик)
    formsetContainer.addEventListener('click', function (event) {
        if (event.target.closest('.delete-form-btn')) {
            const card = event.target.closest('.question-set');
            if (card) {
                card.style.display = 'none';
                // Ставим галочку на удаление
                const deleteCheckbox = card.querySelector('input[type="checkbox"][name$="-DELETE"]');
                if (deleteCheckbox) deleteCheckbox.checked = true;
            }
        }
    });
});