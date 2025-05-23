function editBlockInputs(ev){
    block_id = document.getElementById(ev).value;
    if(block_id){
        fetch(`${block_id}/get_edit_block_user_ui`,{
            method:'GET',
            headers:{
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
        })
        .then(response => response.json())
        .then(data =>{
            if(data['status'] == 'success'){
                editInputURL = data['edit_input_params'];
                window.location = editInputURL;
            }
        })
        .catch(error => console.log("ERROR",error));
    }
    else{
        alert("please select a logic block to edit inputs");
    }
}

document.addEventListener('DOMContentLoaded',load_LB_design_input_params);
document.addEventListener('DOMContentLoaded',load_LB_performance_input_params);
document.addEventListener('DOMContentLoaded',load_LB_lifing_input_params);
document.addEventListener('DOMContentLoaded',load_LB_prognostic_input_params)
function load_LB_design_input_params(){
    fetch('get_design_params',{
        method:'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
    })
    .then(response => response.json())
    .then(data => {
        if(data['status'] == 'success'){
            data['input_params'].forEach(record=>{
                addRow('edit-design-params-container',record['param_name'],record['unit'],record['id']);
            });
        }
    })
    .catch(error => console.error('Error:', error));
}
function load_LB_performance_input_params(){
    fetch('get_performance_params',{
        method:'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
    })
    .then(response => response.json())
    .then(data => {
        if(data['status'] == 'success'){
            data['input_params'].forEach(record=>{
                addRow('edit-performance-params-container',record['param_name'],record['unit'],record['id']);
            });
        }
    })
    .catch(error => console.error('Error:', error));
}
function load_LB_lifing_input_params(){
    fetch('get_lifing_params',{
        method:'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
    })
    .then(response => response.json())
    .then(data => {
        if(data['status'] == 'success'){
            data['input_params'].forEach(record=>{
                addRow('edit-lifing-params-container',record['param_name'],record['unit'],record['id']);
            });
        }
    })
    .catch(error => console.error('Error:', error));
}

function load_LB_prognostic_input_params(){
    fetch('get_prognostic_params',{
        method:'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
    })
    .then(response => response.json())
    .then(data => {
        if(data['status'] == 'success'){
            data['input_params'].forEach(record=>{
                addRow('edit-prognostic-params-container',record['param_name'],record['unit'],record['id']);
            });
        }
    })
    .catch(error => console.error('Error:', error));
}


function addRow(containerId,param_name,unit,id) {
    const container = document.getElementById(containerId);
    const row = document.createElement('div');
    row.className = `input-row`;
    row.id = id || "NONE"
    row.innerHTML = `
        <input type="text" value=${param_name || ""}>
        <input type="text" value=${unit || ""}>
        <button id="${containerId.split("-")[1]}" onclick="deleteRow(this)">Delete</button>
    `;
    container.appendChild(row);
}

function deleteRow(button) {
    const row = button.parentElement;
    const row_id = button.parentElement.id;
    const inputType = button.id
    if(inputType === "design"){
        fetch("delete_design_input",{
            method:'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({
                "record_id":row_id,
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data['status'] == 'success'){
                console.log(data)
            }
        })
        .catch(error => console.error('Error:', error));
    }
    else if(inputType === "performance"){
        fetch("delete_performance_input",{
            method:'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({
                "record_id":row_id,
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data['status'] == 'success'){
                console.log(data)
            }
        })
        .catch(error => console.error('Error:', error));
    }
    else if(inputType === "lifing"){
        fetch("delete_lifing_input",{
            method:'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({
                "record_id":row_id,
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data['status'] == 'success'){
                console.log(data)
            }
        })
        .catch(error => console.error('Error:', error));
    }
    else{
        fetch("delete_prognostics_input",{
            method:'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({
                "record_id":row_id,
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data['status'] == 'success'){
                console.log(data)
            }
        })
        .catch(error => console.error('Error:', error));
    }
    row.remove();

}

function save_edited_params(id){
    const inputParamType = id.split("-")[1]
    if(inputParamType == "design"){
        var edited_design_params = [];
        const editDesignParamsContainer = document.getElementById('edit-design-params-container');
        Array.from(editDesignParamsContainer.children).forEach(node=>{
            const temp_design_params = {};
            const record_id = node.id;
            Array.from(node.children).forEach((inputnode,index)=>{
                if(inputnode.tagName != "BUTTON"){
                    if(index == 0){
                        temp_design_params['param_name'] = inputnode.value;
                    }
                    else{
                        temp_design_params['unit'] = inputnode.value;
                        temp_design_params['id'] = record_id;   
                    }
                }
            })
            edited_design_params.push(temp_design_params);
            
        });
        console.log(edited_design_params);
        fetch('put_edited_design_params',{
            method:'POST',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({'design_edited_params': edited_design_params})
        })
        .then(res=>res.json())
        .then(data=>{
            if(data['status'] == 'success'){
                editDesignParamsContainer.innerHTML = "";
            }
        })
        .catch(error=>console.log("Error",error));
    }
    else if(inputParamType == 'performance'){
        var edited_performance_params = [];
        const editPerformanceParamsContainer = document.getElementById('edit-performance-params-container');
        Array.from(editPerformanceParamsContainer.children).forEach(node=>{
            const temp_performance_params = {};
            const record_id = node.id;
            Array.from(node.children).forEach((inputnode,index)=>{
                if(inputnode.tagName != "BUTTON"){
                    if(index == 0){
                        temp_performance_params['param_name'] = inputnode.value;
                    }
                    else{
                        temp_performance_params['unit'] = inputnode.value;
                        temp_performance_params['id'] = record_id;   
                    }
                }
            })
            edited_performance_params.push(temp_performance_params);
        });
        fetch('put_edited_performance_params',{
            method:'POST',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({'performance_edited_params':edited_performance_params})
        })
        .then(res=>res.json())
        .then(data=>{
            if(data['status'] == 'success'){
                editPerformanceParamsContainer.innerHTML = "";
            }
        })
        .catch(error=>console.log("Error",error));
    }
    else if(inputParamType == 'lifing'){
        var edited_lifing_params = [];
        const editLifingParamsContainer = document.getElementById('edit-lifing-params-container');
        Array.from(editLifingParamsContainer.children).forEach(node=>{
            const temp_lifing_params = {};
            const record_id = node.id;
            Array.from(node.children).forEach((inputnode,index)=>{
                if(inputnode.tagName != "BUTTON"){
                    if(index == 0){
                        temp_lifing_params['param_name'] = inputnode.value;
                    }
                    else{
                        temp_lifing_params['unit'] = inputnode.value;
                        temp_lifing_params['id'] = record_id;   
                    }
                }
            })
            edited_lifing_params.push(temp_lifing_params);
        });
        fetch('put_edited_lifing_params',{
            method:'POST',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({'lifing_edited_params':edited_lifing_params})
        })
        .then(res=>res.json())
        .then(data=>{
            if(data['status'] == 'success'){
                editLifingParamsContainer.innerHTML = "";
            }
        })
        .catch(error=>console.log("Error",error));
    }
    else{
        var edited_prognostic_params = [];
        const editPrognosticParamsContainer = document.getElementById('edit-prognostic-params-container');
        Array.from(editPrognosticParamsContainer.children).forEach(node=>{
            const temp_prognostic_params = {};
            const record_id = node.id;
            Array.from(node.children).forEach((inputnode,index)=>{
                if(inputnode.tagName != "BUTTON"){
                    if(index == 0){
                        temp_prognostic_params['param_name'] = inputnode.value;
                    }
                    else{
                        temp_prognostic_params['unit'] = inputnode.value;
                        temp_prognostic_params['id'] = record_id;   
                    }
                }
            })
            edited_prognostic_params.push(temp_prognostic_params);
        });
        fetch('put_edited_prognostic_params',{
            method:'POST',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({'prognostic_edited_params':edited_prognostic_params})
        })
        .then(res=>res.json())
        .then(data=>{
            if(data['status'] == 'success'){
                editPrognosticParamsContainer.innerHTML = "";
            }
        })
        .catch(error=>console.log("Error",error));
    }
}

function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}