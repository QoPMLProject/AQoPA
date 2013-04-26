'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from qopml.interpreter.model.parser import get_parser
from qopml.interpreter.model.store import create as create_store

text = """
functions
{
  fun id() ( creating id of a side );
  fun skey() [ Availability: bitlength, algorithm ] ( compute symmetric key );
  fun nonce() [ Availability: bitlength, algorithm ] ( compute new nounce );
  fun lifetime() ( compute ticket lifetime );
  fun enc(data , key) [ Availability: bitlength, algorithm, mode] ( encrypt the data );
  fun dec(data , key) [ Availability: bitlength, algorithm, mode] ( decrypt the data );
  fun time() (timestamp generating );
  fun newstate(state) ( chenage the  state of the protocol );
  fun finished() ( finished state );
}


equations {
  eq dec(enc(data,K),K) = data;
  eq f1(f2(true,K),K) = false;
}

channels {
  channel ch1,ch2 (0);
  channel ch3,ch4 (*);
  channel ch5,ch6 (100);
}

versions
{
  version 1
  {
    run host TTP(*)
    {
      run TTP1(*)
    }

    run host B(*)
    {
      run B1(Bv1)
    }

    run host A(*)
    {
      run A1(Av1)
    }
  }


  version 2
  {
    run host TTP(*)
    {
      run TTP1(*)
    }

    run host B(*)
    {
      run B1(Bv2)
    }

    run host A(*)
    {
      run A1(Av2)
    }
  }

}
"""


debug = False

def main():
    
    if debug:
        store = create_store()
        parser = get_parser(store)
        parser.lexer.input(text)
        while True:
            tok = parser.lexer.token()
            if not tok:
                break
            print tok
    
    store = create_store()
    
    parser = get_parser(store)
    parser.parse(text)
    
    for o in store.functions:
        print unicode(o)
    for o in store.channels:
        print unicode(o)
    for o in store.equations:
        print unicode(o)

if __name__ == '__main__':
    main()