function getInputsFromUserLBUI(ev){
    const userSelectLogicBlockBVal =  document.getElementById(ev).value;
    if(userSelectLogicBlockBVal){
        fetch(`${userSelectLogicBlockBVal}/get_block_user_inputs_ui`,{
            method:"GET",
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(res=>res.json())
        .then(data=>{
            if(data['status']=='success'){
                const url = data['user_input_url']
                window.location = url
            }
        })
        .catch(error=>console.log("ERROE:",error))
    }
    else{
        alert("Please select a logic block to enter inputs")
    }
}

// add row and delete row for params

function addRow(containerId) {

    const container = document.getElementById(containerId);
    const row = document.createElement('div');
    row.className = `input-row`;
    row.innerHTML = `
        <input type="text" placeholder="Parameter Name" >
        <input type="text" placeholder="Unit">
        <button onclick="deleteRow(this)">Delete</button>
    `;
    container.appendChild(row);
}

// Function to delete a row
function deleteRow(button) {
    const row = button.parentElement;
    row.remove();
}

// Add an initial row in each section
document.addEventListener('DOMContentLoaded', () => {
    addRow('design-params-container');
    addRow('performance-params-container');
    addRow('lifing-params-container');
    addRow('prognostic-params-container');
});


function save_params(id){
    const typeInput = id.split('-')[0];
    if(typeInput === 'design'){
        var design_params = []
        const designParamsContainer = document.getElementById('design-params-container');
        Array.from(designParamsContainer.children).forEach(node=>{
            const temp_design_params = {};
            Array.from(node.children).forEach((inputnode,index)=>{
                if(inputnode.tagName != "BUTTON"){
                    if(index == 0){
                        temp_design_params['param_name'] = inputnode.value;
                    }
                    temp_design_params['unit'] = inputnode.value;
                }
            })
            design_params.push(temp_design_params);
        });
        fetch("put_design_params",{
            method:'POST',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({
                'design_params':design_params
            })
        })
        .then(res=>res.json())
        .then(data=>{
            if(data['status'] == 'success'){
                designParamsContainer.innerHTML = "";
            }
        })
        .catch(error=>console.log("Error",error))
    }
    else if(typeInput === 'performance'){
        var performance_params = []
        const performanceParamsContainer = document.getElementById('performance-params-container');
        
        Array.from(performanceParamsContainer.children).forEach(node=>{
            const temp_performance_params = {};
            Array.from(node.children).forEach((inputnode,index)=>{
                if(inputnode.tagName != "BUTTON"){
                    console.log(inputnode.tagName);
                    if(index == 0){
                        temp_performance_params['param_name'] = inputnode.value;
                    }
                    temp_performance_params['unit'] = inputnode.value;
                }
            })
            performance_params.push(temp_performance_params);
        });
        fetch("put_preformance_params",{
            method:'POST',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({
                'performance_params':performance_params
            })
        })
        .then(res=>res.json())
        .then(data=>{
            if(data['status'] == 'success'){
                performanceParamsContainer.innerHTML = "";
            }
        })
        .catch(error=>console.log("Error",error))
    }
    else if(typeInput === 'lifing'){
        var lifing_params = []
        const lifingParamsContainer = document.getElementById('lifing-params-container');
        
        Array.from(lifingParamsContainer.children).forEach(node=>{
            const temp_lifing_params = {};
            Array.from(node.children).forEach((inputnode,index)=>{
                if(inputnode.tagName != "BUTTON"){
                    console.log(inputnode.tagName);
                    if(index == 0){
                        temp_lifing_params['param_name'] = inputnode.value;
                    }
                    temp_lifing_params['unit'] = inputnode.value;
                }
            })
            lifing_params.push(temp_lifing_params);
        });
        fetch("put_lifing_params",{
            method:'POST',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({
                'lifing_params':lifing_params
            })
        })
        .then(res=>res.json())
        .then(data=>{
            if(data['status'] == 'success'){
                lifingParamsContainer.innerHTML = "";
            }
        })
        .catch(error=>console.log("Error",error))
    }
    else{
        var prognostic_params = []
        const prognosticParamsConatiner = document.getElementById('prognostic-params-container');
        
        Array.from(prognosticParamsConatiner.children).forEach(node=>{
            const temp_prognostic_params = {};
            Array.from(node.children).forEach((inputnode,index)=>{
                if(inputnode.tagName != "BUTTON"){
                    console.log(inputnode.tagName);
                    if(index == 0){
                        temp_prognostic_params['param_name'] = inputnode.value;
                    }
                    temp_prognostic_params['unit'] = inputnode.value;
                }
            })
            prognostic_params.push(temp_prognostic_params);
        });
        fetch("put_prognostic_params",{
            method:'POST',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({
                'prognostic_params':prognostic_params
            })
        })
        .then(res=>res.json())
        .then(data=>{
            if(data['status'] == 'success'){
                prognosticParamsConatiner.innerHTML = "";
            }
        })
        .catch(error=>console.log("Error",error))
    }
}



function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}