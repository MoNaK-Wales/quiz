document.addEventListener('DOMContentLoaded', function () {
    const formsetContainer = document.getElementById('formset-container');
    const emptyFormTemplate = document.getElementById('empty-form-template')?.innerHTML;

    if (!emptyFormTemplate) {
        return;
    }

    const activateForm = (block) => {
        block.style.opacity = '1';
        const inputs = block.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            input.disabled = false;
        });
    };

    const activateFormsetListener = (block) => {
        const firstInput = block.querySelector('input[type="text"], textarea');

        if (!firstInput) return;

        firstInput.addEventListener('input', function handler() {
            activateForm(block);
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

        const inputs = newBlock.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.disabled = true;
        });

        activateFormsetListener(newBlock);
    };

    formsetContainer.addEventListener('click', function (event) {
        const deleteButton = event.target.closest('.delete-form-btn');
        if (deleteButton) {
            const formSetBlock = deleteButton.closest('.question-set');
            formSetBlock.style.display = 'none';
            const deleteCheckbox = formSetBlock.querySelector('input[type="checkbox"][name*="-DELETE"]');
            if (deleteCheckbox) {
                deleteCheckbox.checked = true;
            }
        }
    });


    const existingBlocks = formsetContainer.querySelectorAll('.question-set');
    
    if (existingBlocks.length > 0) {
        existingBlocks.forEach(block => {
            if (block.style.opacity !== '0.5') {
                activateForm(block);
            }
        });
        activateFormsetListener(existingBlocks[existingBlocks.length - 1]);
    } else {
        addGhostForm(); 
    }
});