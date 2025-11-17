document.addEventListener('DOMContentLoaded', function () {
    const formsetContainer = document.getElementById('formset-container');
    const emptyFormTemplate = document.getElementById('empty-form-template')?.innerHTML;

    if (!emptyFormTemplate) {
        return;
    }

    const activateFormsetListener = (block) => {
        const firstInput = block.querySelector('input[type="text"], textarea');

        if (!firstInput) return;

        firstInput.addEventListener('input', function handler() {
            block.style.opacity = '1';
            addGhostForm();
        }, { once: true });
    };

    const addGhostForm = () => {
        const totalFormsInput = document.getElementById('id_questions-TOTAL_FORMS');
        let currentFormCount = parseInt(totalFormsInput.value);
        const newFormHTML = emptyFormTemplate.replace(/__prefix__/g, currentFormCount);
        
        formsetContainer.insertAdjacentHTML('beforeend', newFormHTML);
        totalFormsInput.value = currentFormCount + 1;
        document.getElementById('id_answers-TOTAL_FORMS').value = currentFormCount + 1;

        const newBlock = formsetContainer.lastElementChild;
        activateFormsetListener(newBlock);
    };

    formsetContainer.addEventListener('click', function (event) {
        if (event.target.classList.contains('delete-form-button')) {
            const formSetBlock = event.target.closest('.formset-block');
            formSetBlock.style.display = 'none';
            const deleteCheckbox = formSetBlock.querySelector('input[type="checkbox"][name*="questions-"][name$="-DELETE"]');
            if (deleteCheckbox) {
                deleteCheckbox.checked = true;
            }
        }
    });


    const existingBlocks = formsetContainer.querySelectorAll('.question-set');
    if (existingBlocks.length === 0) {
        addGhostForm();
    } else {
        activateFormsetListener(existingBlocks[existingBlocks.length - 1]);
    }
});