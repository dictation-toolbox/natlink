// create_natlink_cpp.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include <combaseapi.h>
const wchar_t natlink_clsid_str[] = L"{dd990001-bb89-11d2-b031-0060088dc929}";
const wchar_t x_str[] = L"{f7a1eb9e-049e-4aa4-a742-94cb04551f2d}";
CLSID x_clsid;
//. X AppID {A1F40596-9860-4B32-8032-75CC8D211AB9}
//dragon site object HKEY_LOCAL_MACHINE\SOFTWARE\Classes\WOW6432Node\AppID\{dd100006-6205-11cf-ae61-0000e8a28647}
const wchar_t dgn_site_str[] = L"{dd100006-6205-11cf-ae61-0000e8a28647}";
CLSID natlink_clsid;
CLSID dgn_site_clsid;

#include <atlbase.h>
#include <string>
void hr_check(HRESULT hr, std::string msg)
{
    std::cout << msg << " HRESULT: " << hr << std::endl;
    if (hr < 0)
    {
        exit(hr);
    }

}
int main1()
{
    HRESULT hr0 = CoInitialize(0);
    hr0 = CLSIDFromString(x_str, &x_clsid);

    std::cout << "x clsid str " << x_str;
    IUnknown* pUnk = 0;

    int method = CLSCTX_ALL;
   // int method = CLSCTX_LOCAL_SERVER;

    HRESULT hr1 = CoCreateInstance(x_clsid, 0,method, IID_IUnknown, (void**)&pUnk);
    std::cout << "HR0 " << hr0 << " HR1 " << hr1 << "\npress return";

    std::string str;
    std::getline(std::cin, str);
    return 0;

}   

int main()
{
    HRESULT hr0 = CoInitialize(0);
    hr_check(hr0, "CoInitialize");
    CLSID clsid;
    wchar_t const *  class_string = dgn_site_str;

    auto hr1 = CLSIDFromString(class_string, &clsid);
    hr_check(hr1, "CLSID From String");
    IUnknown* pUnk = 0;
      // int method = CLSCTX_ALL;
    int method = CLSCTX_LOCAL_SERVER;

    HRESULT hr2 = CoCreateInstance(clsid, 0, method, IID_IUnknown, (void**)&pUnk);


    hr_check(hr2, "CoCreateInstance ");

    std::cout << "Press enter";
    std::string str;
    std::getline(std::cin, str);
    return 0;

}

// Run program: Ctrl + F5 or Debug > Start Without Debugging menu
// Debug program: F5 or Debug > Start Debugging menu

// Tips for Getting Started: 
//   1. Use the Solution Explorer window to add/manage files
//   2. Use the Team Explorer window to connect to source control
//   3. Use the Output window to see build output and other messages
//   4. Use the Error List window to view errors
//   5. Go to Project > Add New Item to create new code files, or Project > Add Existing Item to add existing code files to the project
//   6. In the future, to open this project again, go to File > Open > Project and select the .sln file
