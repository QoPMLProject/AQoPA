'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from qopml.interpreter.model.parser import ParserException
from qopml.interpreter.simulator import EnvironmentDefinitionException
from qopml.interpreter.simulator.state import PrintExecutor
from qopml.interpreter.app import Interpreter, Builder
from qopml.interpreter.simulator.error import RuntimeException


text = """
metrics
{
  conf(host1)
  {
    CPU = Intel Core i7-3930K 3.20GHz;
    CryptoLibrary = openssl 0.9.8o-5ubuntu1.2;
    OS = Ubuntu 11.04 64-bit;
  }

  data(host1)
  {
    primhead[function][bitlength][algorithm][mode][Size:ratio];
    primitive[enc][256][AES][CBC][1:1];
    primitive[dec][256][AES][CBC][1:1];
    #
    primhead[function][size:exact(B)];
    primitive[id][8];
    primitive[lifetime][8];
    primitive[time][8];
  }
  
  data+(host1.1)
  {
    primhead[function][bitlength][algorithm][Size:exact(B)];
    primitive[nonce][256][LinuxPRNG][8];
    primitive[skey][256][LinuxPRNG][8];
  }
  
  set host B(host1.1);
  set host TTP(host1.1);
  set host A(host1.1);
  
}

hosts {
  
  host TTP (rr)(*)
  {
    #K_BTTP=skey()[256,LinuxPRNG];
    #K_ATTP=skey()[256,LinuxPRNG];
    
    process TTP1(ch1,ch2)
    {
      x = (a(), b());
      x0 = x[0];
      in(ch1:X);
      K=skey()[256,LinuxPRNG];
      L=lifetime();
      IDA=X[0];
      M2=(K,IDA,L);
      TicketB=enc(M2,K_BTTP)[256,AES,CBC];
      NA=X[2];
      if (NA == X[2]) {
          IDB=X[1];
      } else {
          IDB=X[2];
      }
      M3=(K,NA,L,IDB);
      M3E=enc(M3,K_ATTP)[256,AES,CBC];
      out(ch1:TicketB,M3E);
    }
  }
  
  host A (rr)(*)
  {
    #K_ATTP=skey()[256,LinuxPRNG];
 
    process A1(ch1,ch2)
    {
      IDA = id();
      IDB = id();
      NA = nonce()[256,LinuxPRNG];
      M1 = (IDA, IDB, NA);
      out(ch1:M1);
      in(ch1:TicketB,Y);
      M4=dec(Y,K_ATTP)[256,AES,CBC];
      TA=time();
 
      subprocess Av1(*)
      {
        M5=(IDA,TA);
        K=M4[0];
        authenticator1=enc(M5,K)[256,AES,CBC];
        out(ch2:TicketB, authenticator1);
      }
 
      subprocess Av2(*)
      {
        KA=skey()[256,LinuxPRNG];
        M5=(IDA,TA,KA);
        K=M4[0];
        authenticator2=enc(M5,K)[256,AES,CBC];
        out(ch2:TicketB, authenticator2);
      }
      
      in(ch2:Z);
      M7=dec(Z,K)[256,AES,CBC];
      TArec=M7[0];
      if(TArec==TA){
        status=newstate(finished());
      } else {
        stop;
      }
    }
  }


  host B (rr)(*)
  {
    #K_BTTP=skey()[256,LinuxPRNG];
    process B1(ch2)
    {
      in(ch2:TicketB,authenticator);
      M1=dec(TicketB,K_BTTP)[256,AES,CBC];
      M2=dec(authenticator,K_BTTP)[256,AES,CBC];

      subprocess Bv1(*)
      {
        TA=M2[1];
        K=M1[0];
        M6b=(TA);
        M6=enc(M6b,K)[256,AES,CBC];
        out(ch2:M6);
      }

      subprocess Bv2(*)
      {
        TA=M2[1];
        K=M1[0];
        KB=skey()[256,LinuxPRNG];
        M6b=(TA,KB);
        M6=enc(M6b,K)[256,AES,CBC];
        out(ch2:M6);
      }
    }
  }
}

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
}
"""

"""
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
"""

debug = False

def main():
    
    if debug:
        builder = Builder()
        store = builder.build_store()
        parser = builder.build_parser(store, [])
        parser.lexer.input(text)
        while True:
            print  parser.lexer.current_state()
            tok = parser.lexer.token()
            if not tok:
                break
            print tok
            print ""
        print 'Errors: ' + str(parser.get_syntax_errors())
        print ""
        print ""
    
    
    #####################################
    
    interpreter = Interpreter(builder=Builder())
    try:
        interpreter.set_qopml_model(text)

        """
        interpreter._parse()
        
        store = interpreter.store
        builder = Builder()
        version = store.versions[0]
        simulator = builder.build_simulator(store, version)
        
        for h in simulator.context.hosts:
            print h.name
            for i in h._channels_map:
                print ' - ' + i + ' ' + str([ ch.name for ch in h._channels_map[i] ])
                
            for p in h.instructions_list:
                print ' -- p: ' + p.name
                for i in p._channels_map:
                    print ' ---- ' + i + ' ' + str([ ch.name for ch in p._channels_map[i] ])
        """
        
        interpreter.prepare()
        
        for thread in interpreter.threads: 
            thread.simulator.get_executor().prepend_instruction_executor(PrintExecutor(sys.stdout))
        
            """
            for h in thread.simulator.context.hosts:
                print 
                for p in h.instructions_list:
                    print 
                    for i in p.instructions_list:
                        print unicode(i)
            """
            
        interpreter.run()
    except EnvironmentDefinitionException, e:
        print "Error on creating environment: %s" % e
        if len(e.errors) > 0:
            print "Errors:"
            sys.stderr.write('\n'.join(e.errors))
            print
        return
    except ParserException, e:
        print "Parsing error: %s" % e
        if len(e.syntax_errors):
            print "Syntax errors:"
            sys.stderr.write('\n'.join(e.syntax_errors))
            print
        return
    except RuntimeException, e:
        print "Runtime error: %s" % e
        return
    #####################################
    
    """    
    store = interpreter.store
    
    for o in store.functions:
        print unicode(o)
    for o in store.channels:
        print unicode(o)
    for o in store.equations:
        print unicode(o)
    for o in store.versions:
        print unicode(o)
    for o in store.hosts:
        print unicode(o)
    for o in store.metrics_configurations:
        print unicode(o)
    for o in store.metrics_sets:
        print unicode(o)
    for o in store.metrics_datas:
        print unicode(o)
    for o in store.versions:
        print unicode(o)
    """
    
if __name__ == '__main__':
    main()