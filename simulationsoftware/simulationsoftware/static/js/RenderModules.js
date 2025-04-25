document.addEventListener("DOMContentLoaded", showModules);
document.addEventListener("DOMContentLoaded", showAllSubModules);
document.addEventListener("DOMContentLoaded",showAllLogicBlocks);
function showModules(ev){
    fetch('/admin_panel/retrieveModules',{
        method:'GET',  
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
    })
    .then(response => response.json())
    .then(data => {
        
        const moduleSelect = document.getElementById('moduleSelect');
        
        const moduleSelect1 = document.getElementById('moduleSelect1');
        
        const moduleSelectToDelete = document.getElementById('moduleSelectToDelete')
    

        moduleSelect.innerHTML = ''; // Clear any existing options
        moduleSelect1.innerHTML = '';
        moduleSelectToDelete.innerHTML = '';

        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = '-- Select a Module --';
        placeholderOption.disabled = true;
        placeholderOption.selected = true; // Ensures this option is shown initially
        moduleSelect.appendChild(placeholderOption);

        const placeholderOption1 = document.createElement('option');
        placeholderOption1.value = '';
        placeholderOption1.textContent = '-- Select a Module --';
        placeholderOption1.disabled = true;
        placeholderOption1.selected = true; // Ensures this option is shown initially
        moduleSelect1.appendChild(placeholderOption1);

        const placeholderOption2 = document.createElement('option');
        placeholderOption2.value = '';
        placeholderOption2.textContent = '-- Select a Module --';
        placeholderOption2.disabled = true;
        placeholderOption2.selected = true; // Ensures this option is shown initially
        moduleSelectToDelete.appendChild(placeholderOption2);

        // Check if data.modules is an array
        if (Array.isArray(data.modules) && data.modules.length > 0) {
            // Iterate over the modules and create options for the select dropdown
            data.modules.forEach(module => {
                const option = document.createElement('option');
                const option1 = document.createElement('option');
                const option2 = document.createElement('option');
                option.value = module.id;
                option.textContent = module.name; // Only display module name
                option1.value = module.id;
                option1.textContent = module.name;
                option2.value = module.id
                option2.textContent = module.name
                moduleSelect.appendChild(option);
                moduleSelect1.appendChild(option1);
                moduleSelectToDelete.append(option2);
            }); 
        } else {
            console.error('No modules found');
            // Optionally, show a message if no modules are available
        }
    })
    .catch(error => console.error('Error:', error));
}

function showSubModules(id){
    console.log(id);
    fetch('/admin_panel/retrieveSubModules',{
        method:'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body:JSON.stringify({
                'id':id
            })

    })
    .then(response => response.json())
    .then(data => {
        const subModuleSelect = document.getElementById('submoduleSelect');
        subModuleSelect.innerHTML = '';  // Clear any existing options

        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = '-- Select a SubModule --';
        placeholderOption.disabled = true;
        placeholderOption.selected = true; // Ensures this option is shown initially
        subModuleSelect.appendChild(placeholderOption);

        // Check if data.modules is an array
        if (Array.isArray(data.submodules) && data.submodules.length > 0) {
            // Iterate over the modules and create options for the select dropdown
            data.submodules.forEach(subModule => {
                const option = document.createElement('option');
                option.value = subModule.id;
                option.textContent = subModule.name; // Only display subModule name
                subModuleSelect.appendChild(option);
            });
        } else {
            console.error('No modules found');
            // Optionally, show a message if no modules are available
        }
    })
    .catch(error => console.error('Error:', error));
}

function showAllSubModules(){
    fetch('/admin_panel/retrieveAllSubModules',{
        method:'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
    })
    .then(response => response.json())
    .then(data => {
        const subModuleSelectDelete = document.getElementById('submoduleSelectDelete');
        subModuleSelectDelete.innerHTML = '';  // Clear any existing options

        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = '-- Select a SubModule --';
        placeholderOption.disabled = true;
        placeholderOption.selected = true; // Ensures this option is shown initially
        subModuleSelectDelete.appendChild(placeholderOption);

        // Check if data.modules is an array
        if (Array.isArray(data.allsubmodules) && data.allsubmodules.length > 0) {
            // Iterate over the modules and create options for the select dropdown
            data.allsubmodules.forEach(allsubModule => {
                const option1 = document.createElement('option');
                option1.value = allsubModule.id;
                option1.textContent = allsubModule.name; // Only display subModule name
                subModuleSelectDelete.appendChild(option1);
            });
        } else {
            console.error('No modules found');
            // Optionally, show a message if no modules are available
        }
    })
    .catch(error => console.error('Error:', error));
}

function showAllLogicBlocks(){
    fetch('retrieve_logic_blocks',{
        method:'GET',
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        const blockICOForm = document.getElementById('BlockICOForm');
        const selectElementICOBlock =  blockICOForm.querySelector("#blockSelectICO");
        selectElementICOBlock.innerHTML = '';  // Clear any existing options

        const editBlockICOForm = document.getElementById('editBlockICOForm');
        const selectElementEditICOBlock =  editBlockICOForm.querySelector("#editblockSelectICO")
        selectElementEditICOBlock.innerHTML = '';

        const blockPublishForm = document.getElementById('publishBlock');
        const selectElementPublishBlock = blockPublishForm.querySelector("#blockSelectPublish");
        selectElementPublishBlock.innerHTML = '';

        const selectDeleteLogicBlockElement = document.getElementById("deleteLogicBlockSelect")
        selectDeleteLogicBlockElement.innerHTML = '';

        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = '-- Select a Logic Block --';
        placeholderOption.disabled = true;
        placeholderOption.selected = true; // Ensures this option is shown initially
        selectElementICOBlock.appendChild(placeholderOption);

        const placeholderOptionEdit = document.createElement('option');
        placeholderOptionEdit.value = '';
        placeholderOptionEdit.textContent = '-- Select a Logic Block --';
        placeholderOptionEdit.disabled = true;
        placeholderOptionEdit.selected = true; // Ensures this option is shown initially
        selectElementEditICOBlock.appendChild(placeholderOptionEdit)

        const placeholderOptionPublish = document.createElement('option');
        placeholderOptionPublish.value = '';
        placeholderOptionPublish.textContent = '-- Select a Logic Block --';
        placeholderOptionPublish.disabled = true;
        placeholderOptionPublish.selected = true; // Ensures this option is shown initially
        selectElementPublishBlock.appendChild(placeholderOptionPublish)

        const placeholderOptiondLB = document.createElement('option');
        placeholderOptiondLB.value = '';
        placeholderOptiondLB.textContent = '-- Select a Logic Block --';
        placeholderOptiondLB.disabled = true;
        placeholderOptiondLB.selected = true; // Ensures this option is shown initially
        selectDeleteLogicBlockElement.appendChild(placeholderOptiondLB)


        // Check if data.modules is an array
        if (Array.isArray(data['logicblocks']) && data['logicblocks'].length > 0) {
            // Iterate over the modules and create options for the select dropdown
            data['logicblocks'].forEach(logicblock => {
                const option = document.createElement('option');
                const optionEdit = document.createElement('option');
                const optionPublish = document.createElement('option');
                const optionDLB = document.createElement('option');

                option.value = logicblock['block_id'];
                option.textContent = logicblock['block_name']; // Only display subModule name
                selectElementICOBlock.appendChild(option);

                optionEdit.value = logicblock['block_id'];
                optionEdit.textContent = logicblock['block_name'];
                selectElementEditICOBlock.appendChild(optionEdit);

                optionPublish.value = logicblock['block_id'];
                optionPublish.textContent = logicblock['block_name'];
                selectElementPublishBlock.appendChild(optionPublish);

                optionDLB.value = logicblock['block_id'];
                optionDLB.textContent = logicblock['block_name'];
                selectDeleteLogicBlockElement.appendChild(optionDLB);
            });
        } else {
            console.error('No blocks found');
        }
    })
    .catch(error => console.error('Error:', error));
}
function publish_block(ev){
    const block_id = document.getElementById(ev).value;
    fetch(`${block_id}/publish_block`,{
        method:'GET',
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    })
    .catch(error => console.log("ERROR",error));
}

function editCodeEditor(){
    const val = document.getElementById("blockSelect").value
    fetch('/admin_panel/editCodeEditor',{
        method:"POST",
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body:JSON.stringify({'val':val})
    })
    .then(response => response.json())
    .then(data => {
        if(data['status'] === 'success'){
            const oldCode = (data['data']['code']);
            sessionStorage.setItem("updateCodeBlock",val);
            sessionStorage.setItem("blockCode",oldCode);
            window.location.href = 'codeEditor';
        }
    })
    .catch(error => console.log("Error",error));
}

function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}