from flask import render_template

class HelloController:
    @staticmethod
    def index():
         return render_template("hello.html")