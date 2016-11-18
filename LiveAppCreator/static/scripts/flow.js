var networks = [];

function destroy() {
  if (networks !== null) {
    networks.forEach(network => {
      network.destroy();
    });

    networks = [];
  }
}

function drawAll(events) {
  destroy();

  for (var i = 0; i < events.length; i++) {
    appendHtml(i, events[i].event);
  }

  for (var i = 0; i < events.length; i++) {
    drawEventNetwork(events[i]);
  }
}

function redraw() {
  networks.forEach(network => {
    network.redraw();
    console.log("drawing");
  })
}

function appendHtml(i, name) {
  var element = '<div class="mdl-card on-the-road-again mdl-cell mdl-cell--12-col mdl-shadow--2dp"><div class="mdl-card__media mdl-color-text--grey-50"><h3>' + name + '</h3></div><div class="mdl-color-text--grey-600 mdl-card__supporting-text"><div id="network' + i + '" class="network"></div></div><div class="mdl-card__supporting-text meta mdl-color-text--grey-600"><div class="minilogo"></div><div><strong>Created by Kfir</strong></div></div></div>';

  document.getElementById('cards').innerHTML += element;
}

function drawEventNetwork(event) {
  var nodes = [];
  var edges = [];
  var stepsCount = 0;

  // create the event node
  nodes.push({
    id: 0,
    label: event.event,
    level: 0,
    shape: 'box',
    color: 'rgb(250, 150, 0)'
  });

  // create the steps
  event.steps.forEach(step => {
    nodes.push({id: (stepsCount + 1), level: (stepsCount + 1), label: step.action, shape: 'box'});
    edges.push({from: stepsCount, to: (stepsCount + 1)});
    stepsCount++;
  });

  // create a network
  var container = document.getElementById('network' + networks.length);
  var data = {
    nodes: nodes,
    edges: edges
  };

  var options = {
    edges: {
      smooth: {
        type: 'cubicBezier',
        forceDirection: 'horizontal',
        roundness: 0.4
      },
      arrows: {
        to: {
          enabled: true,
          scaleFactor: 1,
          type: 'arrow'
        }
      },
      shadow: true
    },
    nodes: {
      shadow: true
    },
    layout: {
      hierarchical: {
        direction: 'LR'
      }
    },
    interaction: {
      dragNodes: false
    },
    physics:false
  };

  networks.push(new vis.Network(container, data, options));
  networks[networks.length - 1].moveTo({ scale: 1.55 });
}
