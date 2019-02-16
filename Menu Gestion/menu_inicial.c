#include <string.h>
#include <stdio.h>
#include <stdlib.h>

void imprimirMenu();
int convertirStringANum();
void cargaDeParametros();
void cargaDeParametrosLinear();
void cargaDeParametrosArbol();
void cargaDeParametros3();
void cargaDeParametros4();
void controlInputUsuario();


int main(int argc, char * argv[]) {

  int opcion = -1;
  char * ingreso = NULL;

  do {
    imprimirMenu();
    //Lectura de la entrada del usuario
    scanf("%s", ingreso );
    opcion = convertirStringANum(ingreso); //falla

    switch (opcion) {
      //Linear
      case 1:
        printf("Pedir opciones para parametros");
        break;
      //Abrol
      case 2:
        printf("Pedir opciones para parametros");
        break;
      case 3:
        printf("Pedir opciones para parametros");
        break;
      case 4:
        printf("Pedir opciones para parametros");
        break;

    }

  } while(opcion !=0);


  printf("Fin del programa...\n");
  return 1;
}


void imprimirMenu(){
  printf("- - \tMENU PRINCIPAL\t - - \n");
  printf("Seleccione la topologia deseada o ingrese 0 para salir:\n");

  printf("\t1) Topologia linear.\n");
  printf("\t2) Topologia de arbol.\n");
  printf("\t3) Tolologia    \n");
  printf("\t4) Topologia    \n");

}

int convertirStringANum(char * texto){
  int entero = atoi(texto);
  return entero;
}

void controlInputUsuario(char * msg){
  if (1/* input usuario es invalido */){
    printf("Hubo un error en el input de usuario.\n");
    exit(EXIT_FAILURE);
  }
  else{
    printf("Input correcto...\n" );
  }
}

void cargaDeParametros(int topologiaSeleccionada){
  switch (topologiaSeleccionada) {
    case 1:
      //llamar funcion especifica para lineal
      cargaDeParametrosLinear();
      break;
    case 2:
      //llamar funcion especifica para arbol
      cargaDeParametrosArbol();
      break;
    case 3:
      //Llamar funcion especifica
      cargaDeParametros3();
      break;
    case 4:
    //Llamar funcion especifica
    cargaDeParametros4();
    break;
  }


}

void cargaDeParametrosLinear(){

}

void cargaDeParametrosArbol(){

}

void cargaDeParametros3(){

}

void cargaDeParametros4(){

}
