
var connection = [];
var source = null;
var destination = null;
function startConnection(clickEvent){
    source = clickEvent.target.id.split("_")[0];
    if(clickEvent.target.id.split("-")[1] === "out" && source != null && destination === null){
        connection.push(source);
    }
    else{
        alert("sorry cannot connect."); 
    }
}
function makeConnection(clickEvent){
    destination = clickEvent.target.id.split("_")[0];
    if(clickEvent.target.id.split("-")[1] == "in" && destination != null && source !=null){
        connection.push(destination);
        completeConnection(clickEvent.target.id);
    }
    else{
        destination = null;
        alert("sorry cannot connect");
    }
}
function completeConnection(destinationId){
    fetch('make_block_connection',{
        method:'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            'source_id': connection[0],
            'destination_id': connection[1],
            // destination_type: destinationId.split("_")[1].split("-")[0],
            // id:0
        })
    })
    .then(response => response.json())
    .then((data)=>{
        if(data['status'] === 'success'){
            let connection_id;
            connection_id = data['id'];
            drawLink(source,destination,connection_id);
            source = null;
            destination = null; 
            connection.length = 0;
        }
        else{
            console.log(data['status']);
        }
    })  
    .catch(error => console.error('Error:', error));
}

function removeConnection(lineId){
    fetch('remove_function_block_connection',{
        method:'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            'connection_id' : lineId,
        })
    })
    .then(response => response.json())
    .then(data =>{
        if(data['status'] == 'success'){
            if(data['remove']){
                const lineElement = document.getElementById(lineId);
                lineElement.remove();
                deleteWorkSpacePositionConnection(lineId);
                console.log(workspacePostionState);
            }
            else{
                if(data['redirect']){
                    console.log(data)
                    const message = `data dependency detected (${data['dependent_proxy_name']})...you will be redirected to input values pages...please remove the previous block as "input value from".`
                    alert(message);
                    window.location = data['url'];
                }
            }
        }
        else{
            console.log(data['message']);
        }
    })
    .catch(error => console.error('Error:', error));
    connection.length = 0;
}

function updateLink(srcBlockId,destBlockId,connection_id){
    const connectionElement = document.getElementById(connection_id);
    console.log(connectionElement);

    connectionElement.remove();

    const srcBlock = document.getElementById(srcBlockId+"_function-out");
    const destBlock = document.getElementById(destBlockId+"_function-in");

    console.log(srcBlock);
    console.log(destBlock);

    const svg = document.getElementById("connection-canvas");
    
    const srcRect = srcBlock.getBoundingClientRect();
    const destRect = destBlock.getBoundingClientRect();
    const svgRect = svg.getBoundingClientRect();

    // Calculate the start and end points for the line
    const startX = srcRect.left + srcRect.width / 2 - svgRect.left;
    const startY = srcRect.top + srcRect.height / 2 - svgRect.top; 
    const endX = destRect.left + destRect.width / 2 - svgRect.left;
    const endY = destRect.top + destRect.height / 2 - svgRect.top;

    // Create a line element in SVG
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", startX);
    line.setAttribute("y1", startY);
    line.setAttribute("x2", endX);
    line.setAttribute("y2", endY);
    line.setAttribute("id",connection_id);
    line.setAttribute("stroke", "black");
    line.setAttribute("stroke-width", "2");
    line.setAttribute("marker-end", "url(#arrowhead)");
    line.style.pointerEvents = "auto";
    line.style.cursor = "pointer";

    // Calculate control points for smooth curves
    // const dx = Math.abs(endX - startX) * 0.5; // Half horizontal distance
    // const dy = Math.abs(endY - startY) * 0.5; // Half vertical distance

    // let cx1, cy1, cx2, cy2;

    // if (endX > startX) {
    //     // Forward connection
    //     cx1 = startX + dx;
    //     cy1 = startY;
    //     cx2 = endX - dx;
    //     cy2 = endY;
    // } else {
    //     // Reverse connection (loop-back or crossover)
    //     cx1 = startX - dx;
    //     cy1 = startY - dy;
    //     cx2 = endX + dx;
    //     cy2 = endY + dy;
    // }

    // let path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    // path.setAttribute("d", `M ${startX} ${startY} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${endX} ${endY}`);
    // path.setAttribute("stroke", "black");
    // path.setAttribute("stroke-width", "2");
    // path.setAttribute("fill", "none");
    // path.setAttribute("marker-end", "url(#arrowhead)");
    // path.setAttribute("style", "pointer-events: auto; cursor: pointer;");
    // path.setAttribute("id", connection_id);

    // let path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    // path.setAttribute("stroke", "black");
    // path.setAttribute("stroke-width", "2");
    // path.setAttribute("fill", "none");
    // path.setAttribute("marker-end", "url(#arrowhead)");
    // path.setAttribute("style", "pointer-events: auto; cursor: pointer;");
    // path.setAttribute("id", connection_id);

    // let curvePath;

    // if (Math.abs(startX - endX) < 10 && Math.abs(startY - endY) < 10) {
    //     // **Self-looping connection**
    //     let loopOffset = 40; // Adjust loop size
    //     curvePath = `M ${startX} ${startY} 
    //                  C ${startX + loopOffset} ${startY - loopOffset}, 
    //                    ${startX - loopOffset} ${startY - loopOffset}, 
    //                    ${endX} ${endY}`;
    // } else if (startX < endX) {
    //     // **Forward connection (left to right)**
    //     let dx = (endX - startX) * 0.5;
    //     curvePath = `M ${startX} ${startY} 
    //                  C ${startX + dx} ${startY}, 
    //                    ${endX - dx} ${endY}, 
    //                    ${endX} ${endY}`;
    // } else {
    //     // **Backward/looping connection**
    //     let loopHeight = Math.abs(endY - startY) + 40; // Increase to make it clearer
    //     curvePath = `M ${startX} ${startY} 
    //                  C ${startX - loopHeight} ${startY - loopHeight}, 
    //                    ${endX + loopHeight} ${endY + loopHeight}, 
    //                    ${endX} ${endY}`;
    // }

    // path.setAttribute("d", curvePath);


    svg.appendChild(line);

    line.addEventListener("dblclick",(lineDblClickEvent)=>{
        removeConnection(lineDblClickEvent.target.id)
        // num_connection_for_dest_block(lineDblClickEvent.target.id);
      });
    // Append the line to the SVG canvas
    // svg.appendChild(line);
    updateWorkSpacePositionConnection(connection_id,startX+"px",startY+"px",endX+"px",endY+"px")
    console.log(workspacePostionState);
}
// in use

// function drawLink(srcBlockId,destBlockId,connection_id){
    
//     const srcBlock = document.getElementById(srcBlockId+"_function-out");
//     const destBlock = document.getElementById(destBlockId+"_function-in");

//     const svg = document.getElementById("connection-canvas");
    
//     const srcRect = srcBlock.getBoundingClientRect();
//     const destRect = destBlock.getBoundingClientRect();
//     const svgRect = svg.getBoundingClientRect();

//     // Calculate the start and end points for the line
//     const startX = srcRect.left + srcRect.width / 2 - svgRect.left;
//     const startY = srcRect.top + srcRect.height / 2 - svgRect.top; 
//     const endX = destRect.left + destRect.width / 2 - svgRect.left;
//     const endY = destRect.top + destRect.height / 2 - svgRect.top;
    
//     // Create a line element in SVG
//     // const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
//     // line.setAttribute("x1", startX);
//     // line.setAttribute("y1", startY);
//     // line.setAttribute("x2", endX);
//     // line.setAttribute("y2", endY);
//     // line.setAttribute("id",connection_id);
//     // line.setAttribute("stroke", "black");
//     // line.setAttribute("stroke-width", "2");
//     // line.setAttribute("marker-end", "url(#arrowhead)");
//     // line.style.pointerEvents = "auto"

//     let dx = Math.abs(endX - startX) * 0.5; // Half the horizontal distance
//     let dy = Math.abs(endX - startX) * 0.5; // Half the vertical distance
//     let cx1 = startX + dx; // Control point 1
//     let cy1 = startY - dy; // Curve upwards
//     let cx2 = endX - dx; // Control point 2
//     let cy2 = endY - dy; // Curve upwards

//     let path = document.createElementNS("http://www.w3.org/2000/svg", "path");
//     path.setAttribute("d", `M ${startX} ${startY} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${endY} ${endY}`);
//     path.setAttribute("stroke", "black");
//     path.setAttribute("stroke-width", "2");
//     path.setAttribute("fill", "none");
//     path.setAttribute("marker-end", "url(#arrowhead)");
//     path.setAttribute("style", "pointer-events: auto; cursor: pointer;");
//     path.setAttribute("id", connection_id);

//     svg.appendChild(path);
//     path.addEventListener("dblclick",(lineDblClickEvent)=>{
//         removeConnection(lineDblClickEvent.target.id)
//         // num_connection_for_dest_block(lineDblClickEvent.target.id);
//       });
//     // Append the line to the SVG canvas
//     svg.appendChild(path);
//     setWorkSpacePositionConnection(connection_id,srcBlockId,destBlockId,startX+"px",startY+"px",endX+"px",endY+"px")
//     console.log(workspacePostionState);
// }
function drawLink(srcBlockId, destBlockId, connection_id) {
    const srcBlock = document.getElementById(srcBlockId + "_function-out");
    const destBlock = document.getElementById(destBlockId + "_function-in");

    const svg = document.getElementById("connection-canvas");

    const srcRect = srcBlock.getBoundingClientRect();
    const destRect = destBlock.getBoundingClientRect();
    const svgRect = svg.getBoundingClientRect();

    // Calculate the start and end points
    const startX = srcRect.left + srcRect.width / 2 - svgRect.left;
    const startY = srcRect.top + srcRect.height / 2 - svgRect.top;
    const endX = destRect.left + destRect.width / 2 - svgRect.left;
    const endY = destRect.top + destRect.height / 2 - svgRect.top;

    // Introduce curvature based on distance
    // const dx = Math.abs(endX - startX) * 0.5; // Half horizontal distance
    // const dy = Math.abs(endY - startY) * 0.5; // Half vertical distance

    // let cx1, cy1, cx2, cy2;

    // if (endX > startX) {
    //     // Forward connection
    //     cx1 = startX + dx;
    //     cy1 = startY;
    //     cx2 = endX - dx;
    //     cy2 = endY;
    // } else {
    //     // Reverse connection (loop-back or crossover)
    //     cx1 = startX - dx;
    //     cy1 = startY - dy;
    //     cx2 = endX + dx;
    //     cy2 = endY + dy;
    // }

    // // Create a path element with a curved Bezier connection
    // let path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    // path.setAttribute("d", `M ${startX} ${startY} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${endX} ${endY}`);
    // path.setAttribute("stroke", "black");
    // path.setAttribute("stroke-width", "2");
    // path.setAttribute("fill", "none");
    // path.setAttribute("marker-end", "url(#arrowhead)");
    // path.setAttribute("style", "pointer-events: auto; cursor: pointer;");
    // path.setAttribute("id", connection_id);

    // // Attach dblclick event to remove the connection
    // path.addEventListener("dblclick", (event) => {
    //     removeConnection(event.target.id);
    // });

    // let path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    // path.setAttribute("stroke", "black");
    // path.setAttribute("stroke-width", "2");
    // path.setAttribute("fill", "none");
    // path.setAttribute("marker-end", "url(#arrowhead)");
    // path.setAttribute("style", "pointer-events: auto; cursor: pointer;");
    // path.setAttribute("id", connection_id);

    // let curvePath;

    // if (Math.abs(startX - endX) < 10 && Math.abs(startY - endY) < 10) {
    //     // **Self-looping connection**
    //     let loopOffset = 40; // Adjust loop size
    //     curvePath = `M ${startX} ${startY} 
    //                  C ${startX + loopOffset} ${startY - loopOffset}, 
    //                    ${startX - loopOffset} ${startY - loopOffset}, 
    //                    ${endX} ${endY}`;
    // } else if (startX < endX) {
    //     // **Forward connection (left to right)**
    //     let dx = (endX - startX) * 0.5;
    //     curvePath = `M ${startX} ${startY} 
    //                  C ${startX + dx} ${startY}, 
    //                    ${endX - dx} ${endY}, 
    //                    ${endX} ${endY}`;
    // } else {
    //     // **Backward/looping connection**
    //     let loopHeight = Math.abs(endY - startY) + 40; // Increase to make it clearer
    //     curvePath = `M ${startX} ${startY} 
    //                  C ${startX - loopHeight} ${startY - loopHeight}, 
    //                    ${endX + loopHeight} ${endY + loopHeight}, 
    //                    ${endX} ${endY}`;
    // }

    // path.setAttribute("d", curvePath);
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", startX);
    line.setAttribute("y1", startY);
    line.setAttribute("x2", endX);
    line.setAttribute("y2", endY);
    line.setAttribute("id",connection_id);
    line.setAttribute("stroke", "black");
    line.setAttribute("stroke-width", "2");
    line.setAttribute("marker-end", "url(#arrowhead)");
    line.style.pointerEvents = "auto";
    line.style.cursor = "pointer";

    // Append the path to the SVG canvas
    svg.appendChild(line);
    line.addEventListener("dblclick", (event) => {
        removeConnection(event.target.id);
    });

    // Store position for workspace rendering
    setWorkSpacePositionConnection(
        connection_id, srcBlockId, destBlockId,
        startX + "px", startY + "px", endX + "px", endY + "px"
    );
}

// function num_connection_for_dest_block(lineId){
//     fetch("get_dest_block_num_connections",{
//         method:'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': getCSRFToken()
//         },
//         body:JSON.stringify({
//             "lineId":lineId
//         })
//     })
//     .then(res=>res.json())
//     .then(data=>{
//         if(data['status'] === 'success'){
//             console.log(data['connections'])
//             if(data['message']){
//                 removeConnection(lineId);
//                 // return new Promise((resolve,reject)=>{
                    
//                 // })
//             }
//             else{
//                 alert("There should exist atleast one connection between blocks, Before removing please make a connection with other block and try again.")
//             }
//         }
//         else{
//             console.log(data['message'])
//         }
//     })
//     .catch(error=>console.log("ERROR",error));
// }

function setWorkSpacePositionConnection(connection_id,srcBlockId,destBlockId,startX,startY,endX,endY){
    workspacePostionState.connections_position.push({connection_id,srcBlockId,destBlockId,startX,startY,endX,endY});
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
function updateWorkSpacePositionConnection(connection_id,startX,startY,endX,endY){
    console.log(workspacePostionState);
    const existing_connection = workspacePostionState.connections_position.find(connection => {
        return connection.connection_id === connection_id;
    });
    console.log(existing_connection);
    existing_connection.startX = startX;
    existing_connection.startY = startY;
    existing_connection.endX = endX;
    existing_connection.endY = endY;
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
function deleteWorkSpacePositionConnection(connection_id){
    workspacePostionState.connections_position = workspacePostionState.connections_position.filter(connection => connection.connection_id !== parseInt(connection_id))
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
// function deleteLineKeyboard(ev,lineClickEvent){
//     if(ev.key == 'Delete'){
//         removeConnection(lineClickEvent);
//     }
// }

function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}
