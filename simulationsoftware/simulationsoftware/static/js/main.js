// Toggle function for the the toolbox
document.addEventListener('DOMContentLoaded',loadNetworkCurrentState);
let workspacePostionState = {
    nodes_position:[],
    connections_position:[]
}

function resizeSvgToMatchWorkspace() {
    const workspace = document.getElementById("workspace");
    const svg = document.getElementById("connection-canvas");

    // Get the workspace's dimensions
    const workspaceRect = workspace.getBoundingClientRect();

    // Set the SVG dimensions to match the workspace
    svg.setAttribute("width", workspaceRect.width-10);
    svg.setAttribute("height", workspaceRect.height-10);
}

// Call the function when the page loads
window.addEventListener("load", resizeSvgToMatchWorkspace);

// Adjust dimensions on window resize
window.addEventListener("resize", resizeSvgToMatchWorkspace);

function toggleToolbox() {
    const toolbox = document.getElementById('toolsContainer');
    const workspace = document.getElementById('workspace'); 
    // const showToolboxButton = document.getElementById('showToolboxButton'); not in use

    if (toolbox.classList.contains('collapsed')) {
        toolbox.classList.remove('collapsed');
        workspace.style.marginLeft = '0px';
        // showToolboxButton.style.display = 'none'; not in use
    } else {
        toolbox.classList.add('collapsed');
        workspace.style.marginLeft = '0';

    }
}

var beingDependencies = null;
$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip({
        html : true
    });
    $.ajax({
        url: "getTreeData",  // Replace with the URL of your Django view
        method: "GET",
        success: function (data) {
            let toolbox = $('#myUL'); 
            data.forEach(function (module) {
                // Create module HTML
                let moduleHTML = `<li><span class="caret">${module.name}</span><ul class="nested">`;
                module.submodules.forEach(function (submodule) {
                    // Create submodule HTML
                    let submoduleHTML = `<li><span class="caret">${submodule.name}</span><ul class="nested">`;
                    submodule.logic_blocks.forEach(function (logicBlock) {
                        // Create logic block HTML
                        if(logicBlock.publish)
                            submoduleHTML += `<li><div class="draggable" draggable="true" id="${logicBlock.name}@${logicBlock.id}" blocktype="${logicBlock.blocktype}" mode="${logicBlock.mode}" ondragstart="drag(event)"><div id="display_value" data-toggle="tooltip" title="No parameters set yet" true_id = ${logicBlock.id}>${logicBlock.name}</div></div></li>`;
                    });
                    submoduleHTML += `</ul></li>`;
                    moduleHTML += submoduleHTML;
                });
                moduleHTML += `</ul></li>`;
                toolbox.append(moduleHTML);
            });

            // Initialize tree structure for the nested lists
            $(".caret").on("click", function () {
                // Toggle the visibility of the nested ul
                $(this).next("ul").toggleClass("active");
                // Toggle the caret direction
                $(this).toggleClass("caret-down");
            });
        }
    });
});

function loadNetworkCurrentState(){
    console.log("hello curren network");
    fetch("get_network_current_state",{
        method:'GET',
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
    })
    .then(res=>res.json())
    .then(data=>{
        if(data['status'] === 'success'){
            load_on();
            network_reconstruct_on_refresh(data['state']);
        }
        else{
            console.log("ERROR:",data['message'])
        }
    })
    .catch(error=>console.log('ERROR',error));
}

// Implement the tree view expand/collapse functionality
document.addEventListener("DOMContentLoaded", function () {
    var toggler = document.getElementsByClassName("caret");
    for (var i = 0; i < toggler.length; i++) {
        toggler[i].addEventListener("click", function () {
            this.parentElement.querySelector(".nested").classList.toggle("active");
            this.classList.toggle("caret-down");
        });
    }
});

function openSaveModal() {
    console.log("helllo");
    // Open the Bootstrap modal
    $('#saveNetworkModal').modal('show');
}

// Drag and Drop functionality (same as previous implementation)
function allowDrop(ev) {
    ev.preventDefault();
    const workspace = document.getElementById('workspace');
    workspace.classList.add('drag-over');
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);  
}

function drop(ev) {
    ev.preventDefault();
    const workspace = document.getElementById('workspace');
    workspace.classList.remove('drag-over');
    
    const data = ev.dataTransfer.getData("text");
    const draggedElement = document.getElementById(data);
    
    // newly added
    const workspaceRect = workspace.getBoundingClientRect();
    
    // Calculate position of the drop relative to the workspace
    const xPos = ev.clientX - ev.target.getBoundingClientRect().left;
    const yPos = ev.clientY - ev.target.getBoundingClientRect().top;
    
    // Ensure no duplicate clones exist
    if (!draggedElement.id.includes('Clone')) {
        const clonedElement = draggedElement.cloneNode(true);
        clonedElement.id = data + 'Clone' + Date.now();  // Give unique ID to the clone

        const trueBlockId = data.split("@")[1]
        clonedElement.setAttribute("true_id",trueBlockId);
        workspace.appendChild(clonedElement);
        
        // Position the cloned element
        clonedElement.style.position = 'absolute';
        clonedElement.style.left = (xPos) + 'px';
        clonedElement.style.top = (yPos) + 'px';
        // clonedElement.setAttribute("inputType","None");
        
        // Add a cancel icon on the cloned block
        const cancelIcon = document.createElement('div');
        cancelIcon.classList.add('cancel-icon');
        cancelIcon.innerHTML = 'X';
        clonedElement.appendChild(cancelIcon);

        if(clonedElement.getAttribute('mode') == "function"){
            const blockId = clonedElement.id;
            document.getElementById(blockId).addEventListener('dblclick',(ev)=>{
                load_input_value_user_ondblclick(trueBlockId,blockId);
            });
            put_function_block_clone(clonedElement);
        }
        // else if(clonedElement.getAttribute('mode') === "display"){
        //     makeDataInBlock(clonedElement.id);
        //     // makeDataOutBlock(clonedElement.id);
        //     toSaveRecord(clonedElement);
        // }
        else{
            console.log("sorry")
        }
        // Attach event listener to the cancel icon
        cancelIcon.addEventListener('click', function () {
            delete_function_block_clone(clonedElement)
            clonedElement.remove();
        });
    }
    else {
        // If it's a cloned block, reposition it
        const left = ev.pageX - workspace.offsetLeft - (draggedElement.offsetWidth / 2);
        const top=  ev.pageY - workspace.offsetTop - (draggedElement.offsetHeight / 2);
        draggedElement.style.left = left + 'px';
        draggedElement.style.top = top + 'px';
        updateWorkSpacePostionStateBlock(draggedElement.id,left+"px",top+"px");
        fetch("get_conncetion_existence",{
            method:"POST",
            headers:{
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                "blockId":draggedElement.id
            })
        })
        .then(response => response.json())
        .then(data =>{
            if(data['status'] == 'success'){
                console.log(data['all']);
                data['all'].forEach(conn =>{
                    updateLink(conn['source_id'],conn['destination_id'],conn['id'])
                })
            }
        })
        .catch(error=>console.log("ERROR",error))
        console.log(workspacePostionState);
    }
}

function load_input_value_user_ondblclick(trueBlockId,blockId){
    const actual_block_id = trueBlockId;
    fetch(`${actual_block_id}/${blockId}/get_user_inputs_value_url`,{
        method:'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
    })
    .then(response => response.json())
    .then(data =>{
        if(data['status'] == 'success'){
            window.location = data['url'];
        }
    })
    .catch(error=>console.log("ERROR",error))

}

function openBlockNameModal(ModalId,cloneElement){
    console.log(ModalId);
    console.log(cloneElement);
    $(`#${ModalId}`).modal("show");
    document.getElementById(ModalId).setAttribute("clone-block-id",cloneElement.id);
}

function saveUserBlockName(FormID,ModalId){
    const userBlockNameForm = document.getElementById(FormID);
    const userBlockName = userBlockNameForm.querySelector("#userBlockNameInput").value;
    const cloneBlockId = document.getElementById(ModalId).getAttribute("clone-block-id");
    
    console.log(cloneBlockId);
    if(userBlockName){
        
        userBlockNameForm.querySelector("#userBlockNameInput").value = "";
        fetch("put_function_block_name",{
            method:'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                "user_block_name":userBlockName,
                "clone_id": cloneBlockId,
            })

        })
        .then(response => response.json())
        .then(data =>{
            if(data['status'] == 'success'){
                $(`#${ModalId}`).modal("hide");
                const cloneBlockElement = document.getElementById(cloneBlockId);
                cloneBlockElement.firstChild.textContent = userBlockName;

                setWorkSpacePostionStateBlock(cloneBlockElement.id,userBlockName,cloneBlockElement.getAttribute("true_id"),cloneBlockElement.style.left,cloneBlockElement.style.top);
                console.log(workspacePostionState);
                makeDataInBlock(cloneBlockId);
                makeDataOutBlock(cloneBlockId);
            }
            else{
                alert("name repetition not allowed")
            }
        })
        .catch(error=>console.log("ERROR",error));
    }
    else{
        alert("Please Enter Block Name");
    }
}
    
// Ajax post request to the url to save a record in fucntion table
function put_function_block_clone(clonedElement){
    fetch('put_function_block_clone',{
        method:'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            "id": clonedElement.id,
            "true_id":clonedElement.getAttribute("true_id")
        })
    })
    .then(response => response.json())
    .then(data =>{
        if(data['status'] == 'success'){
            openBlockNameModal("userBlockNameModal",clonedElement);
        }
        else{
            alert("error occured retry again");
        }
    })
    .catch(error => console.error('Error:', error));
}

// Ajax post request to the url to remove a record in fucntion table based on ID
function delete_function_block_clone(element){
    fetch('delete_function_block_clone',{
        method:'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            "id": element.id,
        })
    })
    .then(response => response.json())
    .then(data =>{
        if(data['status'] == 'success'){
            deleteWorkSpacePositionStateBlock(element.id);
            data['connection_ids'].forEach(id=>{
                removeLineOnly(id);
                deleteWorkSpacePositionConnection(id);
            })
            console.log(data);
            console.log(workspacePostionState);
        }
        else{
            console.log(data['message']);
        }
    })
    .catch(error => console.error('Error:', error));
}

function removeLineOnly(id){
    const lineElement = document.getElementById(id)
    lineElement.remove();
    return;
}

function open_network_input_modal(){
    $("#NetworkInputModal").modal('show');
    document.getElementById("NetworkInputTypeModalSelect").addEventListener("change",()=>{
        handleNetworkInputChange();
    })
}

function handleNetworkInputChange(){
    const networkInputForm = document.getElementById("NetworkInputModalForm"); 
    const networkExcelFileElement = networkInputForm.querySelector("#networkExcelFileElement");
    const networkInputType = document.getElementById("NetworkInputTypeModalSelect").value;
    
    if(networkInputType === 'Excel_Upload'){
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.csv, .xls, .xlsx';
        fileInput.className = 'form-control mt-2';
        fileInput.id = 'NetworkexcelFileInput';
        fileInput.multiple = true;
        networkInputForm.firstElementChild.append(fileInput);
    }
    else{
        console.log("sorry");
    }
}

function save_network_excel_csv(){
    const networkInputForm = document.getElementById("NetworkInputModalForm")
    console.log(window.history.state);
    const networkExcelFileElement = networkInputForm.querySelector("#NetworkexcelFileInput");
    if(networkExcelFileElement && networkExcelFileElement.files.length>0){
        const formData = new FormData();
        for (let i = 0; i < networkExcelFileElement.files.length; i++) {
            formData.append('files', networkExcelFileElement.files[i]); 
        }
        fetch("save_network_excel_csv",{
            method:"POST",
            headers:{
                'X-CSRFToken': getCSRFToken()
            },
            body:formData
        })
        .then(response=>response.json())
        .then(data=>{
            if(data['status']=='success'){
                console.log(data['message']);
                $("#NetworkInputModal").modal('hide');
            }
        })
        .catch(error=>console.log("ERROR",error));
    }
}

class RunSimulationIteration{
    constructor(iter){
        this.iter = iter
    }
    get_iter(){
        return this.iter;
    }
}
function open_iteration_modal(modalId){
    $(`#${modalId}`).modal('show');
}

var iter_obj;
function iteration(modalId,elementInputId){ 
    console.log(elementInputId);
    const iter = document.getElementById(elementInputId).value;
    iter_obj = new RunSimulationIteration(iter);
    closeIterationModal(modalId);
}
function closeIterationModal(modalId){
    $(`#${modalId}`).modal('hide');
}

function runSimulation(){
    console.log(iter_obj.get_iter());
    if(iter_obj.get_iter()){
        fetch('run_simulation',{
            method:'POST',
            headers:{
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({
                "iter":parseInt(iter_obj.get_iter())
            })
        })
        .then(response => response.json())
        .then((data) =>{
            if(data.status == 'success'){
                const cmdOutElement = document.getElementById('commandOutput');
                const successSimulation = document.createElement('div');

                successSimulation.textContent = "--- simulation Completed and blocks outputs are below ---"
                successSimulation.classList.add('out-sim-success');
                cmdOutElement.appendChild(successSimulation);
                console.log(data['res']['all_blocks_outs'])
                data['res']['all_blocks_outs'].forEach(blockOut=>{
                    const blockNameDiv = document.createElement('div');
                    blockNameDiv.textContent = `******Block ${blockOut['blockProxyName']}******`;
                    blockNameDiv.classList.add('out');
                    cmdOutElement.appendChild(blockNameDiv);
                    blockOut['outputs'].forEach((out,index)=>{
                        const iterationDiv = document.createElement('div');
                        iterationDiv.textContent = `--- Iteration ${index} Ouputs ---`;
                        iterationDiv.classList.add('out-iteration');
                        cmdOutElement.append(iterationDiv);
                        const out_array = Object.entries(out);
                        out_array.forEach(ele=>{
                            const outBlock = document.createElement('div');
                            console.log(ele);
                            outBlock.textContent = `${ele[0]} : ${ele[1]}`;
                            outBlock.classList.add('out-success');
                            cmdOutElement.appendChild(outBlock);
                            cmdOutElement.scrollTop = cmdOutElement.scrollHeight;
                        })
                        
                    })
                })
            }
            else{
                alert(`${data['message']} "please remove the cycle or upload intial values for the inputs of metioned the block."`);
            }
        })
        .catch(error => console.error('Error:', error));
    }
    else{
        alert("Please enter the number of iterations.")
    }
}


// to save network defined by user
function saveNetwork(save_network_form_id){
    const saveNetworkFileForm = document.getElementById(save_network_form_id);
    const saveNetworkFileName = document.querySelector("#networkFileName").value.trim();
    // .document.querySelector("#networkFileName").value.trim();
    if(!saveNetworkFileName){
        alert('Please provide a valid file name.');
        return;
    }
    fetch("save_user_network",{
        method:'POST',
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({            
            "workspacePostionState" : workspacePostionState,
            "myfilename" : saveNetworkFileName
        })
    })
    .then(response => response.json())
    .then((data) => {
        if(data['status'] == 'success'){
            // const jsonData = JSON.stringify(data['network'],null,2);
            // const blob = new Blob([jsonData], { type: "application/json" });

            // // Create an anchor (<a>) element and set its download attribute
            // const link = document.createElement("a");
            // link.href = URL.createObjectURL(blob); // Create a URL for the Blob
            // link.download = saveNetworkFileName +".json"; // Set the default filename for download
    
            // // Trigger the download
            // link.click();
        }
    })
    .catch(error => console.error('Error:', error))
    $('#saveNetworkModal').modal('hide');
}


// to load all the user networks related to network_id
document.addEventListener("DOMContentLoaded",put_networks);
function put_networks(){
    const selectNetworkElement = document.getElementById("networkSelect")
    fetch("get_user_networks",{
        method:'GET',
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
    })
    .then(res=>res.json())
    .then(data=>{
        if(data['status'] == 'success'){
            selectNetworkElement.innerHTML == "";

            const placeHolder = document.createElement("option");
            placeHolder.value = "";
            placeHolder.selected = true;
            placeHolder.disabled = true;
            placeHolder.textContent = "Upload Network"

            selectNetworkElement.appendChild(placeHolder);

            data['network_files'].forEach(networkFile=>{
                const option = document.createElement("option");
                option.value = networkFile;
                option.textContent = networkFile;
                selectNetworkElement.appendChild(option);
            })
        }
    })
    .catch(error=>console.log("ERROR",error));
}

function network_reconstruct_on_refresh(network){
    reconstructNetwork(network,true);
}
function handleNetworkUpload(ev){
    fetch("get_user_selected_network",{
        method:'POST',
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body:JSON.stringify({
            "network_name" : ev.value.trim(),
        })
    })
    .then(res=>res.json())
    .then(data=>{
        if(data["status"] == "success"){
            reconstructNetwork(data['network'],false);
            load_on();
            put_loading_networking(ev.value.trim());
            setTimeout(()=>{
                    log_recon_inputs_values();
                    fetch("load_user_inputs_to_folder",{
                    method:'POST',
                    headers:{
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body:JSON.stringify({
                        "network_name" : ev.value.trim(),
                    })
                })
                .then(res=>res.json())
                .then(data=>{console.log(data)})
                .catch(error=>console.log("ERROR",error));
            },4000);
        }
    })
    .catch(error=>console.log("ERROR",error));
}

function load_on() {
    document.getElementById("overlay").style.display = "block";
    document.getElementById("toggleCommandPrompt").click();
    setTimeout(()=>{
        console.log("off");
        load_off();
    },3000)
  }
  
function load_off() {
    document.getElementById("toggleCommandPrompt").click();
    document.getElementById("overlay").style.display = "none";
}

function clearAllElements(){
    delete_all_workspace_instances();
};

function delete_all_workspace_instances(){
    fetch('clear_all',{
        method:'POST',
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
            },
        body:JSON.stringify({
            'refresh':false
        })
    })
    .then(res=>res.json())
    .then(data=>{
        if(data['status']=='success'){
            console.log(data);
            const children1 = [...workspace.children];
            const connectionCanvas = document.getElementById("connection-canvas");
            Array.from(connectionCanvas.children).forEach((children)=>{
                if(children.tagName!='defs'){
                    children.remove(children);
                }
            })
            // connectionCanvas.innerHTML = "";
            children1.forEach(child => {
                if (child.tagName !== "svg") {
                    workspace.removeChild(child);
                }
            });
            workspacePostionState.connections_position.length = 0;
            workspacePostionState.nodes_position.length = 0;
            console.log(workspacePostionState)
        }
        else{
            console.log(data);
        }
    })
    .catch(error=>console.log("ERROR",error));
};

function put_reconstruct_clone_block(cloneBlock){
    fetch("put_function_block_clone_recon",{
        method:"POST",
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body:JSON.stringify({
            "id" : cloneBlock['blockId'],
            "true_LB_id" : cloneBlock['blockTrueId'],
            "proxy_name" : cloneBlock['blockName']
        })
    })
    .then(res=>res.json())
    .then(data=>{
        if(data['status'] == 'success'){
            log_recon_block(cloneBlock['blockName']);
            creatBlockInUI(cloneBlock);
            console.log(workspacePostionState);
        }
    })
    .catch(error=>console.log("ERROR",error));
}

function complete_connection_reconst(source,destination,connection_id){

    fetch('make_block_connection_reconst',{
        method:'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            "id":connection_id,
            'source_id': source,
            'destination_id': destination,
        })
    })
    .then(response => response.json())
    .then((data)=>{
        if(data['status']=='success'){
            log_recon_connection(data['connection_data']['proxy_src'],data['connection_data']['proxy_dest']);
            drawLink(data['connection_data']['src'],data['connection_data']['dest'],data['connection_data']['id']);         
        }
    })  
    .catch(error => console.error('Error:', error));
}

function reconstructNetwork(networkData,refresh) {
    if (!networkData['nodes_position'] || !networkData['connections_position']) {
        alert("Invalid network data!");
        return;
    }
    const workspace = document.getElementById("workspace");
    try{
        fetch('clear_all',{
            method:'POST',
            headers:{
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({
                "refresh":refresh
            })
        })
        .then(res=>res.json())
        .then(data=>{
            if(data["status"] == 'success'){
                console.log("Database cleared successfully.");
                const workspaceChildren= [...workspace.children];
                const connectionCanvas = document.getElementById("connection-canvas");
                Array.from(connectionCanvas.children).forEach((children)=>{
                    if(children.tagName!='defs'){
                        children.remove(children);
                    }
                })

                // connectionCanvas.innerHTML = "";
                workspaceChildren.forEach(child => {
                    if (child.tagName !== "svg") {
                        workspace.removeChild(child);
                    }
                });

                workspacePostionState.nodes_position.length = 0;
                workspacePostionState.connections_position.length = 0;

                // Recreate blocks
                const cmdOutElement = document.getElementById('commandOutput');
                const consBlocksDiv = document.createElement('div');
                consBlocksDiv.textContent = '--- Constructing Blocks ---'
                consBlocksDiv.classList.add('out');
                cmdOutElement.appendChild(consBlocksDiv);
                for (const blockData of networkData['nodes_position']) {
                    put_reconstruct_clone_block(blockData); // Wait for the block to be saved before continuing
                }
                setTimeout(()=>{
                    const consConnectionDiv = document.createElement('div');
                    consConnectionDiv.textContent = '--- Constructing Connections ---'
                    consConnectionDiv.classList.add('out');
                    cmdOutElement.appendChild(consConnectionDiv);
                    for (const connection of networkData['connections_position']) {
                        complete_connection_reconst(connection['srcBlockId'],connection['destBlockId'],connection['connection_id']); // Wait for each connection to be saved
                    }
                },2000);
                
            }
            else{
                console.error("Failed to clear database:", clearResult.message);
                return;
            }
        })
        .catch(error=>console.log("ERROR",error))
    }
    catch (error) {
        console.error("Error during reconstruction:", error);
    }
}

function creatBlockInUI(block){
    const blockElement = document.createElement("div");
    blockElement.classList.add("draggable");
    blockElement.setAttribute("draggable",true);
    blockElement.id = block['blockId'];
    blockElement.setAttribute("mode","function");
    blockElement.addEventListener('dragstart',(event)=>{
        drag(event);
    });
    blockElement.style.position = 'absolute',
    blockElement.style.left = block['left'];
    blockElement.style.top = block['top'];
    blockElement.innerHTML = `<div>${block['blockName']}</div>`;
    blockElement.setAttribute("true_id",block['blockTrueId']);
    blockElement.addEventListener('dblclick',()=>{
            load_input_value_user_ondblclick(block['blockTrueId'],block['blockId'])
        }
    );
    workspace.appendChild(blockElement);

    cancel_div = document.createElement("div");
    cancel_div.classList.add("cancel-icon");
    cancel_div.textContent = "X";
    cancel_div.addEventListener('click', function () {
        delete_function_block_clone(blockElement);
        blockElement.remove();
    });
    blockElement.appendChild(cancel_div);

    
    makeDataInBlock(blockElement.id);
    makeDataOutBlock(blockElement.id);

    setWorkSpacePostionStateBlock(blockElement.id,block['blockName'],blockElement.getAttribute("true_id"),blockElement.style.left,blockElement.style.top);
    console.log(workspacePostionState);
    return blockElement;
}


function setWorkSpacePostionStateBlock(blockId,blockName,blockTrueId,left,top){
    workspacePostionState.nodes_position.push({blockId,blockName,blockTrueId,left,top})
    fetch('save_network_current_state',{
        method:"POST",
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body:JSON.stringify({
            'state':workspacePostionState
        })
    })
}

function updateWorkSpacePostionStateBlock(blockId,left,top){
    const existingNode = workspacePostionState.nodes_position.find(node=>node.blockId===blockId)
    existingNode.left = left;
    existingNode.top = top;
    fetch('save_network_current_state',{
        method:"POST",
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body:JSON.stringify({
            'state':workspacePostionState
        })
    })
}

function deleteWorkSpacePositionStateBlock(blockId){
    workspacePostionState.nodes_position = workspacePostionState.nodes_position.filter(node => node.blockId !== blockId)
    fetch('save_network_current_state',{
        method:"POST",
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body:JSON.stringify({
            'state':workspacePostionState
        })
    })
}


// window.onload = function() {
//     document.getElementById("downloadNetworkImage").addEventListener("click", function() {
//         // Select the workspace container and the connection canvas (SVG)
//         const workspace = document.getElementById("workspace");
//         const connectionCanvas = document.getElementById("connection-canvas");
//         const body = document.body;  // Capturing the entire body, which includes workspace and connections.

//         // Use html2canvas to capture the entire body as an image (not just workspace)
//         html2canvas(body, {
//             onrendered: function(canvas) {
//                 // Convert the canvas to image URL
//                 const imageUrl = canvas.toDataURL("image/png");

//                 // Create a link to trigger the download
//                 const link = document.createElement("a");
//                 link.href = imageUrl;
//                 link.download = "network_image.png"; // Specify the filename
//                 link.click(); // Trigger the download
//             },
//             logging: true,  // Optional: For debugging
//             useCORS: true,  // Ensures external resources (like images) are included
//             scale: 2,  // Optional: increases image resolution
//             x: 0,  // Optional: Adjust positioning if needed
//             y: 0,  // Optional: Adjust positioning if needed
//         });
//     });
// };
let isResizing = false;
let initialHeight = 0;
let initialMouseY = 0;

const commandPromptContainer = document.getElementById("commandPromptContainer");
const commandOutput = document.getElementById("commandOutput");
const commandHeader = document.querySelector(".command-prompt-header");

function toggleCommandPrompt() {
    const commandPrompt = document.getElementById("commandPromptContainer");
    if (commandPrompt.classList.contains("collapsed")) {
        commandPrompt.classList.remove("collapsed");
    } else {
        commandPrompt.classList.add("collapsed");
    }
}

commandHeader.addEventListener('mousedown', (e) => {
    if (e.offsetY < 40) { // Only allow resizing when clicking the header
        isResizing = true;
        initialMouseY = e.clientY;
        initialHeight = commandOutput.offsetHeight;
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', stopResizing);
    }
});

function handleMouseMove(e) {
    if (isResizing) {
        const mouseMoveY = e.clientY - initialMouseY;
        const newHeight = Math.max(100, initialHeight - mouseMoveY); // Ensure minimum height is 100px
        commandOutput.style.height = newHeight + 'px';
        
        // Move the header up or down based on the output height
        const headerNewPosition = 40 + (initialHeight - newHeight);
        commandHeader.style.top = `${headerNewPosition}px`; // Move the header up
    }
}

function stopResizing() {
    isResizing = false;
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', stopResizing);
};