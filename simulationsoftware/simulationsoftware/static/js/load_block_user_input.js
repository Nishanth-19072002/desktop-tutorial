document.addEventListener("DOMContentLoaded",load_block_inputs);
setTimeout(()=>{
    load_initial_inputs();
},3000);


function load_initial_inputs(){
    fetch("get_block_initial_inputs_populate",{
        method:"GET",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
    })
    .then(response => response.json())
    .then(data => { 
        if(data['status'] == 'success'){
            if(!data['exists']){
                console.log(data['block_inputs'])
                openIntialModal(data['true_block_id'],data['clone_block_id'],data['block_inputs']);
            }
            else{
                openInitialModalExisting(data['data']['inputs_values']);
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

function load_block_inputs(){
    fetch("get_block_inputs_populate",{
        method:"GET",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
    })
    .then(response => response.json())
    .then(data => { 
        if(data['status'] == 'success'){
            if(!data['exists']){
                openModal(data['true_block_id'],data['clone_block_id'],data['block_inputs']);
            }
            else{
                openModalExisting(data['data']['inputs_values']);
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

function openInitialModalExisting(inputValues){
    console.log(inputValues);
    const userInitialValueinputsModal = document.getElementById('user-initial-value-inputs');
    const userInitialValueinputForm = userInitialValueinputsModal.querySelector('#form-user-initial-input-values');
    const userInitialValueInputContainer = userInitialValueinputForm.querySelector("#inputs-intial-container");

    inputValues.forEach((input,index)=>{
        const row = document.createElement("div");
        row.classList.add('row', 'mb-2', 'align-items-center');
        row.innerHTML = `
                <div class="col-md-2">
                    <input type="text" class="form-control" value="${input.param_name}" readonly id="param_name">
                </div>
                <div class="col-md-2">
                    <input type="text" class="form-control" value="${input.unit}" readonly id="unit">
                </div>
                <div class="col-md-2">
                    ${ input.val_from == 'excel' 
                        ?
                        `<select class="form-control" onchange="handle_input_change_initials(this, ${index},'${userInitialValueinputForm.getAttribute("clone_id")}')">
                            <option value="" disabled>Select...</option>
                            <option value="excel" selected>Excel Upload</option>
                        </select>`
                        : input.val_from === 'previous'
                        ?
                        `<select class="form-control" onchange="handle_input_change(this, ${index},'${userInitialValueinputForm.getAttribute("clone_id")}')">
                            <option value="" disabled>Select...</option>
                            <option value="excel">Excel Upload</option>
                            <option value="previous" selected>Previous Block</option>
                            <option value="user">User Wished Value</option>
                        </select>`
                        : input.val_from === 'user'
                        ?
                        `<select class="form-control" onchange="handle_input_change(this, ${index},'${userInitialValueinputForm.getAttribute("clone_id")}')">
                            <option value="" disabled>Select...</option>
                            <option value="excel">Excel Upload</option>
                            <option value="previous">Previous Block</option>
                            <option value="user" selected>User Wished Value</option>
                        </select>`
                        :
                        `<select class="form-control" onchange="handle_input_change(this, ${index},'${userInitialValueinputForm.getAttribute("clone_id")}')">
                            <option value="" selected disabled>Select...</option>
                            <option value="excel">Excel Upload</option>
                            <option value="previous">Previous Block</option>
                            <option value="user">User Wished Value</option>
                        </select>`
                    }
                </div>
                <div class="col-md-6">
                    <div class="d-flex align-items-center" id="value-initial-container-${index}">

                    </div>
                </div>`;

        userInitialValueInputContainer.append(row);
        var valueContainer = document.getElementById(`value-initial-container-${index}`);
        valueContainer.innerHTML = "";

        if(input.val_from == 'excel'){
            console.log("into intialss");
            valueContainer.innerHTML = `
                ${(input.excel_file === "" || undefined ) && (input.excel_column === "" || undefined ) && (input.sheet_name === "" || undefined)
                ?
                `<select id="selected-excel-inital-file-${index}" class="form-control mr-1" onchange="populate_excel_columns(this,'selected-excel-inital-column-${index}','<-- select a column -->')">
                    
                </select>
                <input type="text" class="form-control mr-1" placeholder="Sheet Name" id=sheet-name>
                <select id="selected-excel-inital-column-${index}" class="form-control">
                    
                </select>`
                :
                `<select id="selected-excel-inital-file-${index}" class="form-control mr-1" onchange='populate_excel_columns(this,"selected-excel-inital-column-${index}","<-- select a column -->")'>
                </select>
                <input type="text" class="form-control mr-1" placeholder="Sheet Name" id=sheet-name value = ${input.sheet_name}>
                <select id="selected-excel-inital-column-${index}" class="form-control">
                </select>`
                
            }`;
            populate_excel(`selected-excel-inital-file-${index}`, input.excel_file || "<-- select an Excel -->");
            populate_excel_columns(document.getElementById(`selected-excel-inital-file-${index}`),`selected-excel-inital-column-${index}`,input.excel_column || "<-- select a column -->");

        }
        else if(input.val_from == 'previous'){
            console.log(input.previous_block);
            valueContainer.innerHTML = `
                ${(input.pervious_block === "" || undefined || null)
                ?
                `<select id="selected-previous-block-${index}" class="form-control mr-1" onchange="handle_block_change(this,'selected-previous-b-out-${index}','<-- Select a output -->','')">
                    
                </select>
                <select id="selected-previous-b-out-${index}" class=" form-control mr-1">
                    
                </select>`
                :
                `<select id="selected-previous-block-${index}" class="form-control mr-1" onchange="handle_block_change(this,'selected-previous-b-out-${index}','<-- Select a output -->','')">
    
                </select>
                <select id="selected-previous-b-out-${index}" class=" form-control mr-1">
    
                </select>`
            }`;

            populate_previous_blocks(`selected-previous-block-${index}`,[input.previous_block_proxy,input.previous_block] || ["<-- Select a block -->",""]);
            setTimeout(() => {
                handle_block_change(document.getElementById(`selected-previous-block-${index}`),`selected-previous-b-out-${index}`,input.previous_block_output_proxy,input.previous_block_output || "<-- Select a output -->","");
            }, 1000);
            
        }   
        
    });
}

function openModalExisting(inputValues){
    console.log(inputValues);
    const userValueinputsModal = document.getElementById('user-value-inputs');
    const userValueinputForm = userValueinputsModal.querySelector('#form-user-input-values');
    const userValueInputContainer = userValueinputForm.querySelector("#inputs-container");

    inputValues.forEach((input,index)=>{
        const row = document.createElement("div");
        row.classList.add('row', 'mb-2', 'align-items-center');
        row.innerHTML = `
                <div class="col-md-2">
                    <input type="text" class="form-control" value="${input.param_name}" readonly id="param_name">
                </div>
                <div class="col-md-2">
                    <input type="text" class="form-control" value="${input.unit}" readonly id="unit">
                </div>
                <div class="col-md-2">
                    ${ input.val_from == 'excel' 
                        ?
                        `<select class="form-control" onchange="handle_input_change(this, ${index},'${userValueinputForm.getAttribute("clone_id")}')">
                            <option value="" disabled>Select...</option>
                            <option value="excel" selected>Excel Upload</option>
                            <option value="previous">Previous Block</option>
                            <option value="user">User Wished Value</option>
                        </select>`
                        : input.val_from === 'previous'
                        ?
                        `<select class="form-control" onchange="handle_input_change(this, ${index},'${userValueinputForm.getAttribute("clone_id")}')">
                            <option value="" disabled>Select...</option>
                            <option value="excel">Excel Upload</option>
                            <option value="previous" selected>Previous Block</option>
                            <option value="user">User Wished Value</option>
                        </select>`
                        : input.val_from === 'user'
                        ?
                        `<select class="form-control" onchange="handle_input_change(this, ${index},'${userValueinputForm.getAttribute("clone_id")}')">
                            <option value="" disabled>Select...</option>
                            <option value="excel">Excel Upload</option>
                            <option value="previous">Previous Block</option>
                            <option value="user" selected>User Wished Value</option>
                        </select>`
                        :
                        `<select class="form-control" onchange="handle_input_change(this, ${index},'${userValueinputForm.getAttribute("clone_id")}')">
                            <option value="" selected disabled>Select...</option>
                            <option value="excel">Excel Upload</option>
                            <option value="previous">Previous Block</option>
                            <option value="user">User Wished Value</option>
                        </select>`
                    }
                </div>
                <div class="col-md-6">
                    <div class="d-flex align-items-center" id="value-container-${index}">

                    </div>
                </div>`;

        userValueInputContainer.append(row);
        var valueContainer = document.getElementById(`value-container-${index}`);
        valueContainer.innerHTML = "";

        if(input.val_from == 'excel'){
            valueContainer.innerHTML = `
                ${(input.excel_file === "" || undefined ) && (input.excel_column === "" || undefined ) && (input.sheet_name === "" || undefined)
                ?
                `<select id="selected-excel-file-${index}" class="form-control mr-1" onchange="populate_excel_columns(this,'selected-excel-column-${index}','<-- select a column -->')">
                    
                </select>
                <input type="text" class="form-control mr-1" placeholder="Sheet Name" id=sheet-name>
                <select id="selected-excel-column-${index}" class="form-control">
                    
                </select>`
                :
                `<select id="selected-excel-file-${index}" class="form-control mr-1" onchange='populate_excel_columns(this,"selected-excel-column-${index}","<-- select a column -->")'>
                </select>
                <input type="text" class="form-control mr-1" placeholder="Sheet Name" id=sheet-name value = ${input.sheet_name}>
                <select id="selected-excel-column-${index}" class="form-control">
                </select>`
                
            }`;
            populate_excel(`selected-excel-file-${index}`, input.excel_file || "<-- select an Excel -->");
            populate_excel_columns(document.getElementById(`selected-excel-file-${index}`),`selected-excel-column-${index}`,input.excel_column || "<-- select a column -->");

        }
        else if(input.val_from == 'previous'){
            console.log(input.previous_block);
            valueContainer.innerHTML = `
                ${(input.pervious_block === "" || undefined || null)
                ?
                `<select id="selected-previous-block-${index}" class="form-control mr-1" onchange="handle_block_change(this,'selected-previous-b-out-${index}','<-- Select a output -->','')">
                    
                </select>
                <select id="selected-previous-b-out-${index}" class=" form-control mr-1">
                    
                </select>`
                :
                `<select id="selected-previous-block-${index}" class="form-control mr-1" onchange="handle_block_change(this,'selected-previous-b-out-${index}','<-- Select a output -->','')">
    
                </select>
                <select id="selected-previous-b-out-${index}" class=" form-control mr-1">
    
                </select>`
            }`;

            populate_previous_blocks(`selected-previous-block-${index}`,[input.previous_block_proxy,input.previous_block] || ["<-- Select a block -->",""]);
            setTimeout(() => {
                handle_block_change(document.getElementById(`selected-previous-block-${index}`),`selected-previous-b-out-${index}`,input.previous_block_output_proxy,input.previous_block_output || "<-- Select a output -->","");
            }, 1000);
            
        }   
        
    });
}

function openIntialModal(true_block_id,clone_block_id,inputs){
    const userInitialValueinputsModal = document.getElementById('user-initial-value-inputs');
    const userInitialValueinputForm = userInitialValueinputsModal.querySelector('#form-user-initial-input-values');
    const userInitialValueInputContainer = userInitialValueinputForm.querySelector("#inputs-intial-container");

    userInitialValueInputContainer.innerHTML = "";
    
    inputs.forEach((input,index)=>{
        const row1  = document.createElement("div");
        row1.classList.add('row', 'mb-2', 'align-items-center');
        row1.
        innerHTML = `
                        <div class="col-md-2">
                            <input type="text" class="form-control" value="${input.param_name}" readonly id="param_name">
                        </div>
                        <div class="col-md-2">
                            <input type="text" class="form-control" value="${input.unit}" readonly id="unit">
                        </div>
                        <div class="col-md-2">
                            <select class="form-control" onchange="handle_input_change_initials(this, ${index})">
                                <option value="" selected disabled>Select...</option>
                                <option value="excel">Excel Upload</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <div class="d-flex align-items-center" id="value-initial-container-${index}">
        
                            </div>
                        </div>`;
        userInitialValueInputContainer.append(row1); 
    });
}

function openModal(true_block_id,clone_block_id,inputs){
    const userValueinputsModal = document.getElementById('user-value-inputs');
    const userValueinputForm = userValueinputsModal.querySelector('form');
    const userValueInputContainer = userValueinputForm.querySelector("#inputs-container");

    userValueInputContainer.innerHTML = "";

    inputs.forEach((input,index)=>{
        const row = document.createElement("div");
        row.classList.add('row', 'mb-2', 'align-items-center');

        row.innerHTML = `
                <div class="col-md-2">
                    <input type="text" class="form-control" value="${input.param_name}" readonly id="param_name">
                </div>
                <div class="col-md-2">
                    <input type="text" class="form-control" value="${input.unit}" readonly id="unit">
                </div>
                <div class="col-md-2">
                    <select class="form-control" onchange="handle_input_change(this, ${index})">
                        <option value="selected disabled">Select...</option>
                        <option value="excel">Excel Upload</option>
                        <option value="previous">Previous Block</option>
                        <option value="user">User Wished Value</option>
                    </select>
                </div>
                <div class="col-md-6">
                    <div class="d-flex align-items-center" id="value-container-${index}">

                    </div>
                </div>`;        
        userValueInputContainer.append(row);
          
    });
}

function handle_input_change(selectElement, index) {
    const valueContainer = document.getElementById(`value-container-${index}`);
    valueContainer.innerHTML = ''; // Clear existing fields
    if (selectElement.value === 'excel') {
        valueContainer.innerHTML = `
            <select id="selected-excel-file-${index}" class="form-control mr-1" onchange='populate_excel_columns(this,"selected-excel-column-${index}","<-- select a column -->")'>
                
            </select>
            <input type="text" class="form-control mr-1" placeholder="Sheet Name" id=sheet-name>
            <select id="selected-excel-column-${index}" class="form-control">
                
            </select>
        `;
        populate_excel(`selected-excel-file-${index}`, "<-- select a Excel -->");


    } else if (selectElement.value === 'previous') {
        valueContainer.innerHTML = `
        <select id="selected-previous-block-${index}" class="form-control mr-1" onchange="handle_block_change(this,'selected-previous-b-out-${index}','<-- Select a output -->','')">
            
        </select>
        <select id="selected-previous-b-out-${index}" class=" form-control mr-1">
            
        </select>
    `;
        populate_previous_blocks(`selected-previous-block-${index}`, ["<-- Select a block -->",""] )
    }
    else if (selectElement.value === 'user') {
        valueContainer.innerHTML = `
            <input type="text" class="form-control" placeholder="Enter Value" id="user value">
        `;
    }
}

function handle_input_change_initials(selectElement, index){
    const valueContainer = document.getElementById(`value-initial-container-${index}`);
    valueContainer.innerHTML = ''; // Clear existing fields
    if (selectElement.value === 'excel') {
        valueContainer.innerHTML = `
            <select id="selected-excel-inital-file-${index}" class="form-control mr-1" onchange='populate_excel_columns(this,"selected-excel-inital-column-${index}","<-- select a column -->")'>
                
            </select>
            <input type="text" class="form-control mr-1" placeholder="Sheet Name" id=sheet-name>
            <select id="selected-excel-inital-column-${index}" class="form-control">
                
            </select>
        `;
        populate_excel(`selected-excel-inital-file-${index}`, "<-- select a Excel -->");

    }
}
function go_back_to_home(){
    fetch("go_back_to_home",{
        method:'GET',
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(res=>res.json())
    .then(data=>{
        if(data['status'] == 'success'){
            window.location.href = data['url'];
        }
    })
    .catch(error => console.log("ERROR",error));
}

function populate_previous_blocks(id,BlockDetails){
    fetch("get_function_block_dependencies",{
        method:'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
    })
    .then(res=>res.json())
    .then(data=>{
        if(data['status'] == 'success'){

            const previousSelectElement = document.getElementById(id);
            previousSelectElement.innerHTML = "";
            const placeholderOption = document.createElement('option');

            console.log(BlockDetails);
            if(Array.isArray(BlockDetails)){
                console.log(BlockDetails[0]);
                placeholderOption.value = BlockDetails[1];
                placeholderOption.disabled = true;
                placeholderOption.selected = true;
                placeholderOption.textContent = BlockDetails[0];
            }
            previousSelectElement.appendChild(placeholderOption);

            data['dependencies'].forEach((dependency)=>{
                const option = document.createElement('option');
                option.value = dependency['clone_id'];
                option.textContent = dependency['proxy_name'];
                option.setAttribute("name",dependency['proxy_name']);
                previousSelectElement.appendChild(option);
                console.log(option.textContent);
            })
        }
    })
    .catch(error => console.log("ERROR",error));
}

function populate_excel(id,ExcelName){

    const element = document.getElementById(id);
    element.innerHTML = "";

    const placeholderOption = document.createElement('option');
    placeholderOption.value = ExcelName;
    placeholderOption.disabled = true;
    placeholderOption.selected = true;
    placeholderOption.textContent = ExcelName;
    element.appendChild(placeholderOption);
    
    fetch("get_network_excel_uploads",{
        method:'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
    })
    .then(response => response.json())
    .then(data =>{
        if(data['status'] == 'success'){
            console.log(data); 
            data['files'].forEach(file=>{
                const option = document.createElement('option');
                option.value = file;
                option.textContent = file;
                element.appendChild(option);
            });
        }
        else{
                console.error('Failed to fetch files:', data['message']);
            }
    })
    .catch(error => console.error('Error:', error));
}

function populate_excel_columns(excelElement,id,defaultColumn){
    console.log(id);
    const element = document.getElementById(id);
    const excelName = excelElement.value;

    element.innerHTML = "";
    const option = document.createElement('option');
    option.value = defaultColumn;
    option.selected = true;
    option.disabled = true;
    option.textContent = defaultColumn;
    element.append(option);
    
    fetch("get_user_selected_excel_columns",{
        method:'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            'excel_name':excelName
        })
    })
    .then(response => response.json())
    .then(data =>{
        if(data['status'] == 'success'){
            data['columns'].forEach(col=>{
                const option = document.createElement('option');
                option.textContent = col;
                option.value = col;
                element.appendChild(option);
                console.log(option.textContent);
            })
        }
        else{
            console.error('Failed to fetch columns:', data['message']);
        }
    })
    .catch(error => console.error('Error:', error));
}

function handle_block_change(previousSelect,outSelectId,defaultDisplay,defaultValue){
    console.log(previousSelect);
    console.log(previousSelect.value);
    const previousBlockID = previousSelect.value;
    const outputSelectElement = document.getElementById(outSelectId);
    fetch("get_blocks_outputs",{
        method:"POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body:JSON.stringify({
            "previous_block_id" : previousBlockID
        })
    })
    .then(response => response.json())
    .then(data =>{
        if(data['status'] == 'success'){
            console.log(data)
            outputSelectElement.innerHTML = "";

            const placeholderOption = document.createElement('option');
            placeholderOption.value = defaultValue;
            placeholderOption.disabled = true;
            placeholderOption.selected = true;
            placeholderOption.textContent = defaultDisplay;
                
            outputSelectElement.appendChild(placeholderOption);

            data['outputs'].forEach(out=>{
                console.log(out);
                const option = document.createElement('option');
                option.textContent = `${out['param_name']}(${out['unit']})`;
                option.value = out['id'];

                outputSelectElement.appendChild(option);
            })
        }
    })
    .catch(error => console.error('Error:', error));
}

function save_block_input_values(inputsContainerId){
    const inputsContainerElement = document.getElementById(inputsContainerId);
    console.log(inputsContainerElement);
    const inputsRows = inputsContainerElement.children;
    var allBlockInputsValues = [];
    Array.from(inputsRows).forEach(inputsRow=>{
        var user_input_values = {};
        var dependent = false;
        const inputsCols = inputsRow.children;
        Array.from(inputsCols).forEach(inputsCol=>{
            Array.from(inputsCol.children).forEach(val=>{
                // console.log(val);
                if(val.children.length === 0){
                    if(val.id.includes("param_name")){
                        user_input_values['param_name'] = val.value;
                    }
                    else if(val.id.includes("unit")){
                        user_input_values['unit'] = val.value;
                    }
                    else{
                        user_input_values['VALUE_NONE'] = "NONE";
                        user_input_values['dependent'] = dependent
                    }
                }
                else{
                    if(val.tagName === 'SELECT'){
                        user_input_values['val_from'] = val.value;
                    }
                    else{
                        Array.from(val.children).forEach(trueVal=>{
                            // console.log(trueVal)
                            if(trueVal.children.length === 0){
                                if(trueVal.id === 'sheet-name'){
                                    user_input_values['sheet_name'] = trueVal.value;
                                }
                                else{
                                    user_input_values['user_value'] = trueVal.value;
                                }
                            }
                            else{
                                if(trueVal.tagName === 'SELECT'){
                                    // console.log(trueVal.id);
                                    if(trueVal.id.includes("excel-file") || trueVal.id.includes("excel-inital-file")){
                                        user_input_values['excel_file'] = trueVal.value;
                                        user_input_values['dependent'] = dependent;
                                    }
                                    else if(trueVal.id.includes("excel-column") || trueVal.id.includes("excel-inital-column")){
                                        user_input_values['excel_column'] = trueVal.value;
                                    }
                                    else if(trueVal.id.includes("previous-block")){
                                        dependent = true;
                                        user_input_values['previous_block'] = trueVal.value;
                                        var proxy_name = null;
                                        Array.from(trueVal.children).forEach(option=>{
                                            if(option.value === trueVal.value){
                                                proxy_name = option.textContent; 
                                            }
                                        })
                                        user_input_values['previous_block_proxy'] = proxy_name;
                                        user_input_values['dependent'] = dependent;
                                    }
                                    else if(trueVal.id.includes("previous-b-out")){
                                        user_input_values["previous_block_output"] = trueVal.value;
                                        var proxy_val = null;
                                        Array.from(trueVal.children).forEach(option=>{
                                            if(option.value === trueVal.value){
                                                proxy_val = option.textContent; 
                                            }
                                        })
                                        user_input_values["previous_block_output_proxy"] = proxy_val;
                                    }
                                    else{
                                        user_input_values["NONE"] = "NONE";
                                    }
                                }
                                else{
                                    console.log("sorry not captured..")
                                }
                            }
                        })
                    }
                }
            })
        })
        allBlockInputsValues.push(user_input_values);
    });
    if(!inputsContainerId.includes("intial")){
        fetch("put_block_input_values",{
            method:"POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({
                "inputs_values" : allBlockInputsValues
            })
        })
        .then(response => response.json())
        .then(data =>{
            if(data['status'] == 'success'){
                // window.history.back();
            }
        })
        .catch(error => console.error('Error:', error));
    }
    else{
        fetch("put_block_initial_input_values",{
            method:"POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({
                "inputs_values" : allBlockInputsValues
            })
        })
        .then(response => response.json())
        .then(data =>{
            if(data['status'] == 'success'){
                // window.history.back();
            }
        })
        .catch(error => console.error('Error:', error));
    }
}
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}