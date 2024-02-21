class Rect {
  constructor(x, y, rotation, width, height, image = "", color = "#ff0000") {
    this.x = x;
    this.y = y;
    this.rotation = rotation;
    this.width = width;
    this.height = height;
    this.img = new Image();
    this.img.src = image;
    this.color = color;
  }

  draw(ctx) {
    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.fillStyle = this.color;
    if (this.img.width != 0) {
      if (this.rotation >= 0 && this.rotation < 4) {
        ctx.rotate(this.rotation * (Math.PI / 2));
        let drawX = 0,
          drawY = 0,
          drawWidth = this.width,
          drawHeight = this.height;

        if (this.rotation === 1 || this.rotation === 3) {
          [drawWidth, drawHeight] = [drawHeight, drawWidth];
          if (this.rotation === 1) drawY = -this.width;
          else drawX = -this.height;
        } else if (this.rotation === 2) {
          drawX = -this.width;
          drawY = -this.height;
        }

        ctx.drawImage(this.img, drawX, drawY, drawWidth, drawHeight);
      }
    } else {
      ctx.fillRect(0, 0, this.width, this.height);
    }
    ctx.restore();
  }
}

class Component {
  constructor(code) {
    console.log(code);
    this.code = code;
    this.name = data[code]["n"];
    this.rect = new Rect(
      100,
      100,
      0,
      data[code]["w"],
      data[code]["h"],
      data[code]["a"],
      data[code]["c"]
    );
    this.pins = data[code]["p"];
    this.dragging = false;
    this.selected = false;
    this.offset_x = 0;
    this.offset_y = 0;
  }

  rotate() {
    this.rect.rotation += 1;
    this.rect.rotation = this.rect.rotation % 4;

    var temp = this.rect.width;
    this.rect.width = this.rect.height;
    this.rect.height = temp;
  }

  move(posX, posY) {
    this.rect.x = posX;
    this.rect.y = posY;
  }

  draw(ctx) {
    if (this.selected) {
      ctx.fillStyle = "#646496";
      ctx.fillRect(
        this.rect.x - 5,
        this.rect.y - 5,
        this.rect.width + 10,
        this.rect.height + 10
      );
    }
    this.rect.draw(ctx);
  }
}

function serialize(obj) {
  if (!(obj.rect instanceof Rect)) {
    throw new TypeError("obj.rect must be a Rect object");
  }
  return JSON.stringify({
    code: obj.code,
    width: obj.rect.width,
    height: obj.rect.height,
    x: obj.rect.x,
    y: obj.rect.y,
    rotation: obj.rect.rotation,
  });
}

function deserialize(js) {
  var DATA = JSON.parse(js);
  var obj = new Component(DATA.code);
  obj.rect = new Rect(
    DATA.x,
    DATA.y,
    DATA.rotation,
    DATA.width,
    DATA.height,
    url + "src/" + obj.code + ".png"
  );
  return obj;
}

function load(str) {
  var jsn = JSON.parse(str);
  var lst = [];
  Connections = jsn.Connections;
  for (var i = 0; i < jsn.Circuit.length; i++) {
    lst.push(deserialize(jsn.Circuit[i]));
  }
  Circuit = lst;
}

function save() {
  var lst = [];
  for (var i = 0; i < Circuit.length; i++) {
    lst.push(serialize(Circuit[i]));
  }
  return JSON.stringify({ Circuit: lst, Connections: Connections });
}

class Button {
  constructor(x, y, h, w, text, action, def, hov) {
    this.rect = new Rect(x, y, 0, h, w, "", def);
    this.text = text;
    this.default = def;
    this.hover = hov;
    this.action = action;
  }

  act(type, mouseX, mouseY) {
    if (type === 0) {
      if (isClicked(mouseX, mouseY, this.rect)) {
        this.rect.color = this.hover;
      } else {
        this.rect.color = this.default;
      }
    }

    if (type === 1) {
      if (isClicked(mouseX, mouseY, this.rect)) {
        this.action();
      }
    }
  }

  draw(ctx) {
    this.rect.draw(ctx);
    ctx.save();
    ctx.font = "bold 20px Arial";
    ctx.fillStyle = "#000000";
    let textX = this.rect.x + this.rect.width / 2;
    let textY = this.rect.y + this.rect.height / 2;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(this.text, textX, textY);
    ctx.restore();
  }
}

class ComponentButton extends Button {
  constructor(x, y, height, width, text, component_id) {
    super(
      x,
      y,
      height,
      width,
      text,
      () => {
        this.createComponent();
      },
      "#1d7874",
      "#134f4c"
    );
    this.component_id = component_id;
  }

  createComponent() {
    let component = new Component(this.component_id);
    Circuit.push(component);
  }
}

class DeleteButton extends Button {
  constructor(x, y, height, width) {
    super(
      x,
      y,
      height,
      width,
      "remove Component",
      () => {
        this.removeComponent();
      },
      "#ff0000",
      "#A52A2A"
    );
  }

  removeComponent() {
    if (Selected != -1) {
      Circuit.splice(Selected, 1);
      var temp = {};
      for (let key in Connections) {
        if (Connections.hasOwnProperty(key)) {
          var value = Connections[key];
          var t = key.substring(0, 1);
          var i = parseInt(key.substring(1));
          console.log(value, t, i);
          if (i != Selected) {
            if (i > Selected) {
              i -= 1;
            }
            var nlist = [];
            value.forEach(function (j) {
              if (j > Selected) {
                nlist.push(j - 1);
              } else if (j < Selected) {
                nlist.push(j);
              }
            });
            temp[t + i] = nlist;
          }
        }
      }
      Connections = temp;
      Selected = -1;
    }
  }
}

function isClicked(mouseX, mouseY, rect) {
  return (
    mouseX >= rect.x &&
    mouseX <= rect.x + rect.width &&
    mouseY >= rect.y &&
    mouseY <= rect.y + rect.height
  );
}

function drawLine(
  ctx,
  startX,
  startY,
  endX,
  endY,
  color = "#000000",
  thickness = 2
) {
  ctx.beginPath();
  ctx.moveTo(startX, startY);
  ctx.lineTo(endX, endY);
  ctx.strokeStyle = color;
  ctx.lineWidth = thickness;
  ctx.stroke();
}

var Circuit = [];
var Connections = {};
var Selected = -1;

$(document).ready(function () {
  var canvas = document.getElementById("Canvas");
  var ctx = canvas.getContext("2d");
  var lastTime = 0;
  var deltaTime = 0;
  let lastScrollTime = 0;

  var Transform = [
    [
      [1, 0.5],
      [0.5, 1],
      [0, 0.5],
      [0.5, 0],
    ],
    [
      [0, 0.5],
      [0.5, 0],
      [1, 0.5],
      [0.5, 1],
    ],
    [
      [0.5, 1],
      [1, 0.5],
      [0.5, 0],
      [0, 0.5],
    ],
  ];

  Circuit = [];
  Connections = {};

  if (json) {
    console.log(json);
    load(json);
  }

  Selected = -1;

  var sidebar_width = 250;
  var button_height = 50;
  var button_margin = 10;
  var button_width = sidebar_width - 2 * button_margin;
  var sidebar_rect = new Rect(
    canvas.width - sidebar_width,
    0,
    0,
    sidebar_width,
    canvas.height,
    "",
    "#071e22"
  );

  var Lclick = true;
  var Rclick = true;
  var Mclick = true;

  var component_buttons = [
    new DeleteButton(
      canvas.width - sidebar_width + button_margin,
      button_margin,
      button_width,
      button_height
    ),
  ];
  var y_pos = 2 * button_margin + button_height;
  for (let key in data) {
    if (data.hasOwnProperty(key)) {
      let value = data[key];
      let button = new ComponentButton(
        canvas.width - sidebar_width + button_margin,
        y_pos,
        button_width,
        button_height,
        "Create " + value["n"],
        key
      );
      component_buttons.push(button);
      y_pos += button_height + button_margin;
    }
  }

  function gameLoop(timestamp) {
    deltaTime = timestamp - lastTime;
    lastTime = timestamp;

    update();
    render();

    requestAnimationFrame(gameLoop);
  }

  function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    var grid = 60;
    for (var x = 0; x < canvas.width; x += grid) {
      drawLine(ctx, x, 0, x, canvas.height, "#c8c8c8");
    }
    for (var y = 0; y < canvas.height; y += grid) {
      drawLine(ctx, 0, y, screen.width, y, "#c8c8c8");
    }
    Circuit.forEach(function (component) {
      component.draw(ctx);
    });

    for (let StartI in Connections) {
      if (Connections.hasOwnProperty(StartI)) {
        let wire = Connections[StartI];
        wire.forEach(function (EndI) {
          var Start = Circuit[parseInt(StartI.substring(1))];
          if (StartI.substring(0, 1) === "a") {
            var StartX =
              Start.rect.x +
              Start.rect.width * Transform[0][Start.rect.rotation][0];
            var StartY =
              Start.rect.y +
              Start.rect.height * Transform[0][Start.rect.rotation][1];
          } else if (StartI.substring(0, 1) === "b") {
            var StartX =
              Start.rect.x +
              Start.rect.width * Transform[2][Start.rect.rotation][0];
            var StartY =
              Start.rect.y +
              Start.rect.height * Transform[2][Start.rect.rotation][1];
          }

          var End = Circuit[EndI];
          var EndX =
            End.rect.x + End.rect.width * Transform[1][End.rect.rotation][0];
          var EndY =
            End.rect.y + End.rect.height * Transform[1][End.rect.rotation][1];

          drawLine(ctx, StartX, StartY, EndX, EndY, "#ff0000", 3);
        });
      }
    }

    sidebar_rect.draw(ctx);
    component_buttons.forEach(function (buttons) {
      buttons.draw(ctx);
    });
  }

  function update() {
    canvas.addEventListener("mousedown", function (event) {
      var mouseX = event.clientX - canvas.getBoundingClientRect().left;
      var mouseY = event.clientY - canvas.getBoundingClientRect().top;
      Circuit.forEach(function (component) {
        if (isClicked(mouseX, mouseY, component.rect)) {
          if (event.button === 0) {
            Select(Circuit.indexOf(component));
            component.offset_x = component.rect.x - mouseX;
            component.offset_y = component.rect.y - mouseY;
          }
        }
      });

      if (Lclick && event.button === 0) {
        component_buttons.forEach(function (butt) {
          butt.act(1, mouseX, mouseY);
        });

        Lclick = false;
      }

      if (Rclick && event.button === 2) {
        if (Selected != -1) {
          Circuit.forEach(function (component) {
            if (isClicked(mouseX, mouseY, component.rect)) {
              if (component.selected === false) {
                var index = Circuit.indexOf(component);
                if (Connections.hasOwnProperty("a" + Selected)) {
                  if (Connections["a" + Selected].includes(index)) {
                    Connections["a" + Selected].splice(
                      Connections["a" + Selected].indexOf(index),
                      1
                    );
                  } else {
                    Connections["a" + Selected].push(index);
                  }
                } else {
                  Connections["a" + Selected] = [index];
                }
              } else {
                Circuit[Selected].rotate();
              }
            }
          });
        }

        Rclick = false;
      }

      if (Mclick && event.button === 1) {
        event.preventDefault();
        if (Selected != -1) {
          Circuit.forEach(function (component) {
            if (
              isClicked(mouseX, mouseY, component.rect) &&
              Circuit[Selected].pins > 2
            ) {
              if (component.selected === false) {
                var index = Circuit.indexOf(component);
                if (Connections.hasOwnProperty("b" + Selected)) {
                  if (Connections["b" + Selected].includes(index)) {
                    Connections["b" + Selected].splice(
                      Connections["b" + Selected].indexOf(index),
                      1
                    );
                  } else {
                    Connections["b" + Selected].push(index);
                  }
                } else {
                  Connections["b" + Selected] = [index];
                }
              } else {
                Circuit[Selected].rotate();
              }
            }
          });
        }

        Mclick = false;
      }
    });

    canvas.addEventListener("mouseup", function (event) {
      var mouseX = event.clientX - canvas.getBoundingClientRect().left;
      var mouseY = event.clientY - canvas.getBoundingClientRect().top;

      Circuit.forEach(function (component) {
        if (event.button === 0) {
          component.dragging = false;
        }
      });

      if (event.button === 0) {
        Lclick = true;
      }
      if (event.button === 2) {
        Rclick = true;
      }
      if (event.button === 1) {
        Mclick = true;
      }
    });

    canvas.addEventListener("mousemove", function (event) {
      var mouseX = event.clientX - canvas.getBoundingClientRect().left;
      var mouseY = event.clientY - canvas.getBoundingClientRect().top;
      var isWithinCanvas =
        mouseX >= 0 &&
        mouseY >= 0 &&
        mouseX <= canvas.width &&
        mouseY <= canvas.height;
      if (Selected != -1) {
        if (Circuit[Selected].dragging && isWithinCanvas) {
          Circuit[Selected].move(
            mouseX + Circuit[Selected].offset_x,
            mouseY + Circuit[Selected].offset_y
          );
        }
      }
      component_buttons.forEach(function (butt) {
        butt.act(0, mouseX, mouseY);
      });
    });

    canvas.addEventListener("wheel", function (event) {
      const currentTime = Date.now();
      const timeDiff = currentTime - lastScrollTime;
      const scrollThreshold = 10;
      if (timeDiff >= scrollThreshold) {
        lastScrollTime = currentTime;
        var mouseX = event.clientX - canvas.getBoundingClientRect().left;
        var mouseY = event.clientY - canvas.getBoundingClientRect().top;
        if (isClicked(mouseX, mouseY, sidebar_rect)) {
          if (event.deltaY < 0) {
            if (component_buttons[0].rect.y < 10) {
              component_buttons.forEach(function (button) {
                button.rect.y += 10;
              });
            }
          } else if (event.deltaY > 0) {
            if (
              component_buttons[component_buttons.length - 1].rect.y >
              canvas.height - 60
            ) {
              component_buttons.forEach(function (button) {
                button.rect.y -= 10;
              });
            }
          }
        }
      }
    });
  }

  function Select(index) {
    Circuit.forEach(function (cur) {
      cur.selected = false;
      cur.dragging = false;
    });
    Circuit[index].selected = true;
    Circuit[index].dragging = true;
    Selected = index;
  }

  requestAnimationFrame(gameLoop);
});

function sendSave() {
  fetch("/save", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(save()),
  })
    .then((response) => {
      if (!response.ok) {
      }
      window.location.reload();
      return response.json();
    })
    .then((data) => {})
    .catch((error) => {});
}
