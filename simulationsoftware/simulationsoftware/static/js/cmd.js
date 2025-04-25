function processCommand(event) {
    commands = [
        {"run":"Run command is used to execute the built network which is in workspace."},
        {"upload":"Load command ask to upload a JSON file in which the network is saved."},
        {"clear network":"clear network command is used to earse network in workspace and related datas."},
        {"cls":"cls command is used to clear the console screen."},
        {"show cmds": "view all the commands available."}
    ]
    if (event.key === 'Enter') {
        var acceptCmd = false;
        const input = document.getElementById('commandInput');
        const output = document.getElementById('commandOutput');
        const command = input.value;

        if (command.trim() === "") 
            return; // Prevent empty commands

        else (commands.forEach((cmd)=>{
            Object.keys(cmd).forEach((key)=>{
                if(key===command.trim()){
                    acceptCmd = true;
                    return;
                }
            })
        }))
        if(acceptCmd === true){
            const commandElement = document.createElement('div');
            commandElement.textContent = `>> ${command}`;
            output.appendChild(commandElement);

            // Process command (add your own logic here)
            if(command.split(" ")[0]==="upload"){
                document.getElementById("networkFileInput").click()
                console.log("hi");
            }
            else if(command === "run"){
                runSimulation()
            }
            else if(command === "clear network"){
                document.getElementById("clearNetwork").click();
            }
            else if(command === "cls"){
                output.innerHTML = "";
            }
        }
        else{
            const notAvailableCmd = document.createElement("div");
            notAvailableCmd.textContent = ">> Command not found. Use one of the following.";
            output.append(notAvailableCmd);
            commands.forEach((cmd)=>{
                Object.keys(cmd).forEach((key,index)=>{
                    const showCmdElement = document.createElement('div');
                    showCmdElement.textContent =`${index}. command:${key}, description:${cmd[key]}`;
                    output.append(showCmdElement);
                })
            })
        }  
        // Clear input
        input.value = '';
        // Scroll to bottom
        output.scrollTop = output.scrollHeight;
    }
}

function put_loading_networking(fileName){
    const output = document.getElementById('commandOutput');
    const commandElement = document.createElement('div');
    commandElement.classList.add('out');
    commandElement.textContent = `Loading --> ${fileName} Network. Please Wait...`;
    output.appendChild(commandElement);
    output.scrollTop = output.scrollHeight;
}

function log_recon_block(blockName){
    const output = document.getElementById('commandOutput');
    const commandElement = document.createElement('div');
    commandElement.textContent = `${blockName}`;
    commandElement.classList.add('out-success');
    output.appendChild(commandElement);
    output.scrollTop = output.scrollHeight;
}

function log_recon_connection(srcName,destName){
    const output = document.getElementById('commandOutput');
    const commandElement = document.createElement('div');
    commandElement.textContent = `${srcName} -> ${destName}`;
    commandElement.classList.add('out-success');
    output.appendChild(commandElement);
    output.scrollTop = output.scrollHeight;
}

function log_recon_inputs_values(){
    const output = document.getElementById('commandOutput');
    const commandElement = document.createElement('div');
    commandElement.classList.add('out');
    commandElement.textContent = `--- Populating Blocks Inputs Values ---`;
    output.appendChild(commandElement);
    output.scrollTop = output.scrollHeight;
}