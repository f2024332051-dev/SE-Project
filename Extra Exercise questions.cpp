#include <iostream>
using namespace std;

class student{
private:
    string name;
    int roll;
public:
    student(){
        cout<<"Default Constructor Called"<<endl;
    }
    student(string n, int r){
        name = n;
        roll = r;
    }
    void display(){
        cout<<"Name: "<<name<<"\tRollNo: "<<roll<<endl;
    }

    ~student(){
        cout<<"Destructor Called\n";
    }
};

int main(){
    student s1,s2("Ali", 32);
    student s3("Rayyan", 20);
    s2.display();
    s3.display();
return 0;
}

