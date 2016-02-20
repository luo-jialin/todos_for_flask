$(function(){

  var Todo = Backbone.Model.extend({
    defaults: function() {
      return {
        title: "empty todo...",
        order: Todos.nextOrder(),
        done: false
      };
    },

    toggle: function() {
      this.save(
        {done: !this.get("done")},
        {
          wait: true,
          success: function(todo, response){
            todo.set({'done': response['done']});
          }
        }
      );
    },

    parse: function(response){
      return response;
    }

  });

  var TodoList = Backbone.Collection.extend({
    url: '/fetch_todos',
    model: Todo,

    done: function() {
      return this.where({done: true});
    },

    remaining: function() {
      return this.where({done: false});
    },

    nextOrder: function() {
      if (!this.length) {
        return 1;
      }
      return this.last().get('order') + 1;
    },

    parse: function(response){
        return response.data;
    },

    comparator: 'order'

  });

  // Create our global collection of **Todos**.
  var Todos = new TodoList;

  var TodoView = Backbone.View.extend({

     tagName: "li",

     template: _.template($("#item-template").html()),

     events: {
      "click .toggle"      : "toggleDone",
      "dblclick .view"      : "edit",
      "keypress .edit"     : "updateOnEnter",
      "blur .edit"         : "close",
      "click .destroy"     : "clear"
     },

      initialize: function(){
        this.listenTo(this.model, "change", this.render);
        this.listenTo(this.model, "destroy", this.remove);
      },

      render: function(){
        this.$el.html(this.template(this.model.toJSON()));
        this.$el.toggleClass("done", this.model.get("done"));
        this.input = this.$(".edit");
        return this;
      },

      toggleDone: function(){
        this.model.toggle();
      },

      edit: function(){
        this.$el.addClass("editing");
        this.input.focus();
      },

      updateOnEnter: function(e){
        if(e.keyCode == 13)
          this.close();
      },

      close: function(){
        var val = this.input.val();
        if(!val){
          this.clear();
        }else{
          this.model.save(
            {title: val},
            {
              wait: true,
              success: function(todo, response){
                todo.set({'title': response['title']})
            }
          }
          );
          this.$el.removeClass("editing");
        }
      },

      clear: function(){
        this.model.destroy({
          wait: true,
          success: function(model, response){
            console.log(response)
          },
          error: function(model, response){
            console.log(" clear model error")
            console.log(response)
          }
        });
      }
  });

  var AppView = Backbone.View.extend({

     el: $("#todoapp"),
     statsTemplate: _.template($('#stats-template').html()),

    events: {
                   "keypress #new-todo"    : "createOnEnter",
                    "click #toggle-all"     : "toggleAllComplete",
                    "click #clear-completed": "clearAllComplete",
    },
     initialize: function(){
      this.input = this.$("#new-todo");
      this.allCheckbox = this.$("#toggle-all")[0];

      this.main = this.$("#main");
      this.footer = this.$("footer");

      this.listenTo(Todos, "all", this.render);
      this.listenTo(Todos, "add", this.addOne);
      this.listenTo(Todos, "reset", this.addAll);

      Todos.fetch( );
     },

     flash: function(){
      Todos.fetch();
     },

     render: function(){
      var done = Todos.done().length;
      var remaining = Todos.remaining().length;

      if(Todos.length){
        this.main.show();
        this.footer.show();
        this.footer.html(this.statsTemplate({done: done, remaining: remaining}));
      }else{
        this.main.hide();
        this.footer.hide();
      }
      this.allCheckbox.checked = !remaining;
     },

     addOne: function(todo){
      var view = new TodoView({model: todo});
      this.$("#todo-list").append(view.render().el);
     },

     addAll: function(){
      Todos.each(this.addOne, this);
     },

     createOnEnter: function(e){
      if(e.keyCode == 13){
        if(!this.input.val()){
          return;
        }
        Todos.create(
          {title: this.input.val()},
          {
            wait:true,
            success: function(todo, response){
              todo.set({'id': response['id'], 'title': response['title']});
            }
          }
          );
        this.input.val("");
      }else{
        return;
      }
     },

     toggleAllComplete: function(){
      var done = this.allCheckbox.checked;
      Todos.each(function(todo){
        todo.save({'done': done});
      });
     },

     clearAllComplete: function(){
      _.invoke(Todos.done(), 'destroy');
      return false;
     }

  });
  
  var App  = new AppView;
});