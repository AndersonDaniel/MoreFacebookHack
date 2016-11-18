var network;
var ifNode;
var callNode;
var nodes;
var edges;

function graph() {
	nodes = new vis.DataSet();
  edges = new vis.DataSet();

  // nodes.add({id: 0, label: 'first', data: {kfir: 2}});
  // nodes.add({id: 1, label: 'seconddddddddddddd', shape: 'box'});
  // edges.add({from: 0, to: 1});

  // nodes.add({id: 2, label: 'first'});
  // nodes.add({id: 3, label: 'seconddddddddddddd', shape: 'box'});
  // edges.add({from: 2, to: 3});

  // nodes.add({id: 4, label: 'first'});
  // nodes.add({id: 5, label: 'seconddddddddddddd', shape: 'box'});
  // edges.add({from: 4, to: 5});

  // create a network
  var container = document.getElementById('graph');
  var data = {
    nodes: nodes,
    edges: edges
  };

  var options = {
    edges: {
      smooth: {
        type: 'cubicBezier',
        roundness: 0.4
      },
      arrows: {
      	to: true
      }
    },
    nodes: {
    	shape: "box",
    	borderWidth: 0,
      value: 10,
    	scaling: {
    		min: 15,
    		max: 30,
    		label: {
    			enabled: true,
    			min: 15,
    			max: 30
    		}
    	},
    	font: {
    		color: "#ffffff"
    	},
      color: {
      	background: '#f57c00',
      	border: '#f57c00'
      },
      shapeProperties: {
      	borderRadius: 100
      },
      physics: true
    },
    physics: {
    	solver: 'barnesHut',
	    barnesHut: {
	      gravitationalConstant: -1000,
	      centralGravity: 0.3,
	      springLength: 150,
	      springConstant: 0.04,
	      damping: 0.09,
	      avoidOverlap: 0.7
	    },
    }
  };

  network = new vis.Network(container, data, options);

  network.on('doubleClick', e => {
  	if (e.nodes[0] && e.edges[0]) showPopup(e.nodes[0], e.edges[0]);
  });

  document.getElementById('cancel').onclick = function() {
  	document.getElementById('card').style.display = "none";
  }

  document.getElementById('save').onclick = function() {
  	var condition = document.getElementById('textCondition').value;
  	var type = document.getElementById('serviceType').value;
  	var method = document.getElementById('serviceMethod').value;
  	var URL = document.getElementById('textURL').value;
  	var param = document.getElementById('textParameters').value;

  	var dataBlock = {
  		condition,
  		type,
  		method,
  		URL,
  		param
  	};

  	document.getElementById('card').style.display = "none";

  	addCouple(dataBlock);
  }

  document.getElementById('addNode').onclick = function() {
  	// var condition = document.getElementById('textCondition');
  	// var type = document.getElementById('serviceType');
  	// var method = document.getElementById('serviceMethod');
  	// var url = document.getElementById('textURL');
  	// var params = document.getElementById('textParameters');

  	document.getElementById('textCondition').value = "";
  	document.getElementById('serviceType').value = "";
  	document.getElementById('serviceMethod').value = "";
  	document.getElementById('textURL').value = "";
  	document.getElementById('textParameters').value = "";

  	document.getElementById('card').style.display = "block";
  }

  document.getElementById('saveInteractions').onclick = function() {
    var interactions = exportData();

    var post = new Http.Post("../submit", interactions, true);
    post.start().then(res => {
      console.log("updated the server");
    });
  }
}

function addCouple(interaction) {
  nodes.add([
    {id: nodes.length, label: interaction.condition + ' [' + interaction.type + '/' + interaction.method +']', data: interaction}, 
    {id: (nodes.length + 1), label: interaction.URL + ' (' + interaction.param + ')', shape: 'box'}]);

  edges.add([{from: (nodes.length - 2), to: (nodes.length - 1)}]);
}

function showPopup(node, edge) {
	var nodeFromId = network.body.data.edges.get(edge).from;
	var nodeToId = network.body.data.edges.get(edge).to;

	ifNode = network.body.data.nodes.get(nodeFromId);
	callNode = network.body.data.nodes.get(nodeToId);

	document.getElementById('textCondition').value = ifNode.label;
	document.getElementById('textURL').value = callNode.label;

  document.getElementById('card').style.display = "";
}

function importData(interactions) {
	interactions.forEach(interaction => {
		addCouple(interaction);
  });
}

function exportData() {

	var interactions = [];

	edges.forEach(edge => {
		interactions.push(nodes.get(edge.from).data);
	});

	return interactions;
}