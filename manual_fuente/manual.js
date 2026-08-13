const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, HeadingLevel, AlignmentType,
  PageBreak, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  LevelFormat, Footer, PageNumber, Tab, TabStopType, LeaderType,
} = require("docx");

// Paleta corporativa: los mismos valores que usa la aplicación
// (COLOR_* de configuracion.py y aplicacion.py), sin el '#' que docx no lleva.
const AZUL = "152342";          // COLOR_AZUL      — azul corporativo
const AZUL_CLARO = "1A2E5A";    // COLOR_AZUL_HOVER
const AZUL_SUAVE = "5A6B8C";    // azul grisáceo de los textos secundarios
const SUBTITULO = "C7D2E6";     // COLOR_SUBTITULO — sobre fondo azul
const GRIS_FONDO = "F0F2F5";    // COLOR_GRIS_CLARO
const GRIS_FILA = "F7F8FA";     // COLOR_CAMPO     — filas alternas
const BORDE = "E1E5EC";         // COLOR_BORDE
const BORDE_FUERTE = "CBD2DE";  // COLOR_BORDE_CAMPO
const PUNTEADO = "C3C9D4";      // guías de puntos del índice
const TEXTO = "152342";         // COLOR_TEXTO
const BLANCO = "FFFFFF";
// Colores de los estados, iguales a los de la pestaña Oficios.
const POR_ASIGNAR = "B45309";   // COLOR_POR_ASIGNAR
const EN_PROCESO = "1D4ED8";    // COLOR_EN_PROCESO
const FINALIZADO = "15803D";    // COLOR_FINALIZADO

// Logo recortado y repintado sobre el azul exacto por logo.py, para que se
// funda con la banda azul de la portada sin que se note el recuadro.
const LOGO = __dirname + "/logo_portada.png";
const LOGO_PROPORCION = 5.54;

// Identificación del documento: la versión del manual y la de la aplicación
// que documenta son independientes y se indican por separado.
const VERSION_APLICACION = "1.0";
const VERSION_DOCUMENTO = "2.0";
const FECHA_ELABORACION = "13 de agosto de 2026";

// ---------- Ayudantes ----------
const TEXTO_CUERPO = "232B3D";   // gris azulado, más cálido que el negro puro

const p = (texto, opts = {}) => new Paragraph({
  alignment: opts.alignment,
  spacing: { after: opts.after === undefined ? 120 : opts.after, line: 276 },
  indent: opts.indent,
  border: opts.border,
  keepNext: opts.juntar,
  children: [new TextRun({
    text: texto,
    bold: opts.bold, italics: opts.italics,
    size: opts.size || 22,
    color: opts.color || TEXTO_CUERPO,
    font: "Calibri",
  })],
});

// Párrafo con partes en negrita: [["normal ", false], ["negrita", true]]
const pMix = (partes, opts = {}) => new Paragraph({
  spacing: { after: opts.after === undefined ? 120 : opts.after, line: 276 },
  indent: opts.indent,
  children: partes.map(([texto, negrita]) => new TextRun({
    text: texto, bold: !!negrita, size: opts.size || 22,
    color: opts.color || TEXTO_CUERPO, font: "Calibri",
  })),
});

// Los títulos se van anotando aquí para construir el índice sin campos de Word
// (un índice automático se ve vacío hasta que el lector actualiza los campos).
const ENTRADAS = [];

const h1 = (texto) => {
  ENTRADAS.push({ texto, nivel: 0 });
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 10, color: AZUL, space: 8 } },
    children: [new TextRun({ text: texto, bold: true, size: 32, color: AZUL, font: "Calibri" })],
  });
};

const h2 = (texto) => {
  ENTRADAS.push({ texto, nivel: 1 });
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 140 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: BORDE, space: 5 } },
    children: [new TextRun({ text: texto, bold: true, size: 26, color: AZUL_CLARO, font: "Calibri" })],
  });
};

const h3 = (texto) => new Paragraph({
  heading: HeadingLevel.HEADING_3,
  spacing: { before: 200, after: 100 },
  children: [new TextRun({ text: texto, bold: true, size: 23, color: AZUL_SUAVE, font: "Calibri" })],
});

const vinieta = (texto, nivel = 0) => new Paragraph({
  numbering: { reference: "vinetas", level: nivel },
  spacing: { after: 80, line: 276 },
  children: [new TextRun({ text: texto, size: 22, color: TEXTO_CUERPO, font: "Calibri" })],
});

// Cada llamada a pasos() usa una instancia de numeración distinta, para que
// las listas de pasos empiecen en 1 y no continúen la cuenta de la anterior.
let _instanciaPasos = 0;
const pasos = (textos) => {
  const instancia = _instanciaPasos++;
  return textos.map((texto) => new Paragraph({
    numbering: { reference: "pasos", level: 0, instance: instancia },
    spacing: { after: 80, line: 276 },
    children: [new TextRun({ text: texto, size: 22, color: TEXTO_CUERPO, font: "Calibri" })],
  }));
};

// Recuadro de aviso. Por defecto lleva la barra azul corporativa; con
// { tono: "aviso" } se pinta en ámbar, el mismo color con el que la aplicación
// marca lo que exige atención (COLOR_POR_ASIGNAR).
const aviso = (titulo, texto, opts = {}) => {
  const acento = opts.tono === "aviso" ? POR_ASIGNAR : AZUL;
  const fondo = opts.tono === "aviso" ? "FDF6EC" : GRIS_FONDO;
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    borders: {
      top: { style: BorderStyle.SINGLE, size: 2, color: BORDE_FUERTE },
      bottom: { style: BorderStyle.SINGLE, size: 2, color: BORDE_FUERTE },
      left: { style: BorderStyle.SINGLE, size: 18, color: acento },
      right: { style: BorderStyle.SINGLE, size: 2, color: BORDE_FUERTE },
      insideHorizontal: { style: BorderStyle.NONE },
      insideVertical: { style: BorderStyle.NONE },
    },
    rows: [new TableRow({
      cantSplit: true,
      children: [new TableCell({
        width: { size: 9360, type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: fondo },
        margins: { top: 120, bottom: 120, left: 180, right: 180 },
        children: [new Paragraph({
          spacing: { after: 0, line: 276 },
          children: [
            new TextRun({ text: titulo + "  ", bold: true, size: 22, color: acento, font: "Calibri" }),
            new TextRun({ text: texto, size: 22, color: TEXTO_CUERPO, font: "Calibri" }),
          ],
        })],
      })],
    })],
  });
};

const espacio = (alto = 120) => new Paragraph({ spacing: { after: alto }, children: [] });

// Tabla con cabecera azul y filas alternas.
// Una celda puede ser una cadena o { texto, color, negrita } para resaltarla
// (por ejemplo, los estados con su color de la pestaña Oficios).
function tabla(cabeceras, filas, anchos) {
  const total = anchos.reduce((a, b) => a + b, 0);
  const celda = (valor, opts = {}) => {
    const { texto, color, negrita } = typeof valor === "string"
      ? { texto: valor } : valor;
    return new TableCell({
      width: { size: opts.ancho, type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: opts.fondo || BLANCO },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({
        spacing: { after: 0, line: 264 },
        alignment: opts.centrar ? AlignmentType.CENTER : undefined,
        // keepNext en todas las filas menos la última mantiene la tabla
        // entera en la misma página en lugar de partirla por la mitad.
        keepNext: !opts.ultima,
        children: [new TextRun({
          text: texto,
          bold: negrita === undefined ? opts.negrita : negrita,
          size: 20,
          color: color || opts.color || TEXTO_CUERPO,
          font: "Calibri",
        })],
      })],
    });
  };

  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: anchos,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: AZUL },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: AZUL },
      left: { style: BorderStyle.SINGLE, size: 2, color: BORDE_FUERTE },
      right: { style: BorderStyle.SINGLE, size: 2, color: BORDE_FUERTE },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: BORDE },
      insideVertical: { style: BorderStyle.SINGLE, size: 2, color: BORDE },
    },
    rows: [
      new TableRow({
        tableHeader: true,
        cantSplit: true,
        children: cabeceras.map((c, i) =>
          celda(c, { ancho: anchos[i], negrita: true, fondo: AZUL, color: BLANCO, centrar: i > 0 })),
      }),
      ...filas.map((fila, n) => new TableRow({
        cantSplit: true,
        children: fila.map((c, i) => celda(c, {
          ancho: anchos[i],
          centrar: i > 0,
          fondo: n % 2 ? GRIS_FILA : BLANCO,
          ultima: n === filas.length - 1,
        })),
      })),
    ],
  });
}

const saltoPagina = () => new Paragraph({ children: [new PageBreak()] });

// ---------- PORTADA ----------
// Banda azul corporativa que ocupa el ancho útil de la página. El logo lleva
// exactamente ese mismo azul de fondo, así que se funde con la banda.
const ANCHO_LOGO = 330;   // puntos; la altura sale de la proporción del PNG

const bandaAzul = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [9360],
  borders: {
    top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
    left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
    insideHorizontal: { style: BorderStyle.NONE },
    insideVertical: { style: BorderStyle.NONE },
  },
  rows: [new TableRow({
    children: [new TableCell({
      width: { size: 9360, type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: AZUL },
      margins: { top: 560, bottom: 560, left: 240, right: 240 },
      children: [
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 260 },
          children: [new ImageRun({
            type: "png",
            data: fs.readFileSync(LOGO),
            transformation: {
              width: ANCHO_LOGO,
              height: Math.round(ANCHO_LOGO / LOGO_PROPORCION),
            },
          })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 0 },
          children: [new TextRun({
            text: "UNIDAD DE CUMPLIMIENTO",
            size: 22, color: SUBTITULO, font: "Calibri", characterSpacing: 80,
          })],
        }),
      ],
    })],
  })],
});

const portada = [
  espacio(900),
  bandaAzul,
  espacio(560),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 100 },
    children: [new TextRun({ text: "MANUAL DE USUARIO", size: 28, color: AZUL_SUAVE, font: "Calibri", characterSpacing: 60 })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 300 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: AZUL, space: 14 } },
    children: [new TextRun({ text: "Control de Oficios", bold: true, size: 60, color: AZUL, font: "Calibri" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 60 },
    children: [new TextRun({ text: "Sistema de registro y seguimiento de oficios y circulares", size: 22, color: AZUL_SUAVE, font: "Calibri", italics: true })],
  }),
  espacio(1500),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 60 },
    children: [new TextRun({
      text: `Aplicación versión ${VERSION_APLICACION}`,
      bold: true, size: 22, color: TEXTO_CUERPO, font: "Calibri",
    })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 60 },
    children: [new TextRun({
      text: `Documento versión ${VERSION_DOCUMENTO}`,
      size: 22, color: TEXTO_CUERPO, font: "Calibri",
    })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 120 },
    children: [new TextRun({
      text: `Actualizado el ${FECHA_ELABORACION}`,
      size: 22, color: AZUL_SUAVE, font: "Calibri",
    })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "USO INTERNO", bold: true, size: 20, color: POR_ASIGNAR, font: "Calibri", characterSpacing: 40 })],
  }),
  saltoPagina(),
];

// ---------- CONTENIDO ----------
const contenido = [
  h1("1. Introducción"),
  p("Control de Oficios es la aplicación de la Unidad de Cumplimiento destinada al registro y al seguimiento de los oficios y circulares que recibe el área."),
  p("La aplicación constituye un complemento de la matriz de control utilizada hasta la fecha: centraliza el registro, asigna la numeración de manera automática y permite conocer en todo momento la situación de cada requerimiento, así como la de las personas sobre las que se solicita información."),
  p(`El presente documento corresponde a la versión ${VERSION_APLICACION} de la aplicación y sustituye a las ediciones anteriores del manual.`),

  h2("1.1 Los tres roles"),
  p("Las funciones disponibles dependen del rol asignado a cada cuenta. El manual se ha ordenado de menor a mayor alcance, de modo que cada rol comprende las funciones del anterior e incorpora las propias."),
  tabla(
    ["Rol", "Alcance"],
    [
      ["Usuario", "Registra y atiende los oficios a su cargo"],
      ["Administrador", "Lo anterior, más la gestión de todos los oficios, el mantenimiento y las cuentas"],
      ["Superusuario", "Lo anterior, más la creación de administradores y las copias de seguridad"],
    ],
    [2200, 7160],
  ),
  espacio(200),
  aviso("Importante:", "la primera cuenta que se crea al instalar la aplicación corresponde al superusuario y no puede eliminarse."),

  h1("2. Primeros pasos (todos los roles)"),

  h2("2.1 Ingresar al sistema"),
  ...pasos([
    "Abra la aplicación desde el acceso directo.",
    "Indique su usuario y su contraseña.",
    "Pulse Ingresar.",
  ]),
  p("Cuando la aplicación se utiliza por primera vez, la pantalla inicial solicita la creación de la cuenta de superusuario en lugar del ingreso habitual."),

  h2("2.2 Cambiar su propia contraseña"),
  p("Toda persona puede modificar su contraseña por sí misma, con independencia de su rol:"),
  ...pasos([
    "Pulse Cambiar contraseña, en la cabecera de la ventana.",
    "Indique su contraseña actual.",
    "Escriba la nueva contraseña y confírmela.",
    "Pulse Cambiar.",
  ]),
  aviso("¿Por qué se solicita la contraseña actual?", "Constituye una medida de seguridad: impide que un tercero la modifique si la sesión permanece abierta."),
  espacio(160),
  p("En caso de haber olvidado la contraseña, deberá solicitarse su restablecimiento a un administrador o al superusuario (apartado 4.7)."),

  h2("2.3 Cerrar sesión"),
  p("Pulse Cerrar sesión en la cabecera y confirme la operación. La aplicación regresa a la pantalla de ingreso, de modo que otra persona pueda acceder con su propia cuenta."),

  h2("2.4 La ventana"),
  p("La aplicación se abre maximizada, ocupando la totalidad de la pantalla. La ventana puede reducirse, ampliarse o restaurarse en cualquier momento mediante los botones habituales; el contenido se acomoda al tamaño elegido."),

  h2("2.5 Las pestañas"),
  tabla(
    ["Pestaña", "Función", "Quién la visualiza"],
    [
      ["Registrar oficio", "Alta de un oficio nuevo", "Todos"],
      ["Oficios", "Consulta, modificación, mantenimiento y exportación", "Todos"],
      ["Tablero", "Indicadores y gráficos", "Todos"],
      ["Usuarios", "Administración de cuentas", "Administrador y superusuario"],
      ["Configuración", "Numeración, tipos de acción, carga masiva y copias de seguridad", "Administrador y superusuario"],
    ],
    [2400, 4360, 2600],
  ),

  saltoPagina(),
  h1("3. Rol Usuario"),
  p("El usuario registra los oficios que le corresponden y les da seguimiento hasta su finalización."),
  aviso("Alcance de la consulta:", "el usuario visualiza únicamente los oficios que ha registrado o que tiene asignados; no accede a los del resto del equipo."),

  h2("3.1 Registrar un oficio"),
  p("En la pestaña Registrar oficio deberá completarse el formulario, organizado en cinco bloques: datos del oficio, asignación y seguimiento, personas investigadas, documentos y observación. Los campos señalados con asterisco (*) son obligatorios."),
  tabla(
    ["Campo", "Obligatorio", "Observaciones"],
    [
      ["Institución del Estado *", "Sí", "Superintendencia de Bancos o Fiscalía General del Estado"],
      ["Referencia oficio *", "Sí", "No admite duplicados"],
      ["Tipo de acción *", "Sí", "Se elige del catálogo del área"],
      ["Causal oficio", "No", "Texto libre"],
      ["Fecha de oficio *", "Sí", "No posterior a la de recepción"],
      ["Fecha de recepción *", "Sí", "—"],
      ["Usuario responsable", "—", "Se asigna automáticamente al usuario"],
      ["Estado *", "Sí", "En proceso o Finalizado"],
      ["Fecha de asignación", "No", "No anterior a la de recepción"],
      ["Fecha de respuesta", "No", "Al indicarla, el oficio se finaliza"],
      ["Prioridad", "No", "Baja, Media o Alta; se propone Media"],
      ["Personas investigadas", "No", "Se detallan en su propio bloque (apartado 3.2)"],
      ["Documento del oficio *", "Sí", "Archivo PDF o Word (.docx)"],
      ["Respuesta en PDF", "No", "Solo para registrar un oficio ya finalizado"],
      ["Observación", "No", "Puede modificarse posteriormente"],
    ],
    [2900, 1700, 4760],
  ),
  espacio(200),
  p("Al guardar, la aplicación asigna automáticamente la Referencia UDC. Dicha referencia no se digita, no se repite y su nomenclatura depende de la institución seleccionada (apartado 6.4)."),
  aviso("El documento es obligatorio:", "no se registra un oficio sin su soporte. Se admite PDF o Word (.docx)."),
  espacio(160),
  aviso("Asignación automática:", "los oficios registrados por un usuario quedan a su cargo. Su asignación a otra persona corresponde a un administrador."),

  h2("3.2 Personas investigadas"),
  p("Un mismo oficio puede solicitar información sobre varias personas, naturales o jurídicas. De cada una se anota:"),
  tabla(
    ["Campo", "Obligatorio", "Observaciones"],
    [
      ["Nombre o razón social *", "Sí", "Persona natural o empresa"],
      ["Tipo de identificación", "No", "Cédula, pasaporte o RUC"],
      ["Identificación", "No", "Si se indica, debe señalarse su tipo"],
      ["Tipo de implicado *", "Sí", "Cliente, No cliente, Ex cliente o Sin identificación"],
      ["LCI *", "Sí", "Lista de Control Interno: Sí o No; se propone No"],
    ],
    [3100, 1700, 4560],
  ),
  espacio(200),
  p("En el formulario de registro, complete los datos de la persona y pulse Añadir persona; el registro se incorpora a la lista y el formulario queda disponible para la siguiente. El botón Quitar retira de la lista a la persona seleccionada."),
  p("Una vez registrado el oficio, las personas se consultan y se modifican con doble clic sobre el oficio, en la pestaña Oficios."),
  aviso("Cantidad de investigados:", "no se digita. La aplicación la obtiene de esta lista y la actualiza cuando se incorpora o se retira a una persona."),

  h2("3.3 Buscar oficios"),
  p("En la pestaña Oficios, el panel Buscar oficios ofrece tres bloques de filtros, que pueden combinarse entre sí."),
  h3("Por texto"),
  p("Seleccione el campo (Referencia UDC, Institución del Estado, Referencia oficio, Tipo de acción o Causal oficio), indique el texto y pulse Buscar. No es necesario escribir el valor completo ni respetar las mayúsculas."),
  h3("Por valor"),
  p("Los desplegables permiten acotar por Institución del Estado, Tipo de acción, Causal, Estado y Prioridad. La opción (Todos) deja de filtrar por ese campo."),
  h3("Por fecha"),
  p("Seleccione el tipo de fecha (de oficio, de recepción, de asignación o de respuesta) y el rango desde–hasta. Ambos extremos corresponden siempre al mismo tipo de fecha. Si el campo hasta se deja en blanco, la búsqueda se realiza por una fecha única."),
  p("El botón Limpiar filtros restablece la lista completa."),

  h2("3.4 Modificar un oficio propio"),
  p("Seleccione el oficio en la lista y utilice el panel Modificar oficio seleccionado. El usuario puede actualizar:"),
  vinieta("La fecha de respuesta"),
  vinieta("El tipo de acción"),
  vinieta("La prioridad"),
  vinieta("El estado, entre En proceso y Finalizado"),
  vinieta("La observación"),
  p("Pulse Guardar cambios para aplicar la modificación. Las personas investigadas se modifican con doble clic sobre el oficio, y la cantidad de investigados se actualiza en consecuencia."),
  aviso("Fecha de respuesta y estado:", "al registrar una fecha de respuesta, el oficio pasa automáticamente a Finalizado. Para reabrirlo, deberá eliminarse previamente esa fecha mediante el botón Limpiar del calendario."),

  h2("3.5 Documentos del oficio"),
  p("Cada oficio conserva dos documentos: el propio oficio, que se adjunta al registrarlo, y la respuesta en PDF, que se incorpora al atenderlo."),
  vinieta("Ver oficio: muestra el documento del oficio. Los archivos PDF se abren dentro de la aplicación; los de Word, con el programa del equipo."),
  vinieta("Cambiar oficio: sustituye el documento, en caso de haberse adjuntado el archivo equivocado."),
  vinieta("Adjuntar respuesta (PDF): incorpora el documento de respuesta."),
  vinieta("Ver respuesta (PDF): permite consultarlo desde la propia aplicación."),
  vinieta("Eliminar PDF: retira la respuesta adjunta."),
  p("La columna PDF de la lista señala con «Sí» los oficios que ya cuentan con su respuesta adjunta."),
  aviso("Para finalizar un oficio:", "constituye requisito que cuente con fecha de asignación, fecha de respuesta y la respuesta en PDF adjunta. Si faltara alguno, la aplicación indica cuál."),

  h2("3.6 Exportar oficios"),
  p("El botón Exportar genera un archivo con los oficios registrados:"),
  ...pasos([
    "Pulse Exportar, en la pestaña Oficios.",
    "Si desea acotar el resultado, seleccione el tipo de fecha y la fecha o el rango correspondiente.",
    "Elija el formato: Excel o CSV.",
    "Indique dónde guardar el archivo.",
  ]),
  p("Si no se indica ninguna fecha, se exporta la totalidad de los oficios que la persona puede consultar. El archivo contiene todos los datos del oficio y dedica una fila a cada persona investigada, con los datos del oficio repetidos, de forma análoga a la matriz del área."),

  h2("3.7 Tablero"),
  p("Presenta los indicadores de gestión del área: total de oficios, distribución por estado, porcentaje de finalizados, días promedio de respuesta, oficios recibidos por día y por mes, y carga por responsable. Para el rol Usuario, el tablero considera únicamente sus propios oficios."),

  saltoPagina(),
  h1("4. Rol Administrador"),
  p("El administrador dispone de las funciones del rol Usuario y, adicionalmente, gestiona los oficios de toda el área, su mantenimiento y las cuentas de acceso."),

  h2("4.1 Ver y gestionar todos los oficios"),
  p("A diferencia del usuario, el administrador visualiza en la pestaña Oficios los registros de todas las personas y dispone, en el panel de modificación, de los siguientes campos:"),
  vinieta("La fecha de asignación"),
  vinieta("La fecha de respuesta"),
  vinieta("El tipo de acción"),
  vinieta("La prioridad"),
  vinieta("El responsable, con posibilidad de reasignar el oficio a cualquier usuario"),
  vinieta("El estado, incluido Por asignar"),
  vinieta("La observación"),
  p("El panel de búsqueda incorpora además el filtro por Responsable, que comprende la opción (Sin responsable). Al registrar un oficio, el administrador puede designar a cualquier responsable o dejarlo sin asignar."),
  aviso("Alcance de la asignación:", "un administrador no puede asignar oficios a un superusuario; esas cuentas no figuran en su lista de responsables. El superusuario sí puede asignarlos a cualquiera."),

  h2("4.2 Mantenimiento de oficios"),
  p("El panel de modificación no permite alterar los datos que identifican al oficio. Cuando alguno se hubiera registrado con un error de digitación, se corrige mediante el botón Mantenimiento, disponible para administradores y para el superusuario."),
  p("Seleccione el oficio y pulse Mantenimiento. Podrán corregirse la Referencia oficio, la Causal, la fecha de oficio y la fecha de recepción. Las correcciones se someten a las mismas validaciones que el registro."),
  h3("Anular un oficio"),
  p("Los oficios no se eliminan: se anulan. Desde la misma ventana, el botón Anular oficio solicita el motivo y retira el registro de la lista y de los indicadores, conservándolo."),
  vinieta("La Referencia UDC no se reutiliza, de modo que la numeración no presenta vacíos sin justificación."),
  vinieta("Queda constancia de quién lo anuló, cuándo y por qué motivo."),
  vinieta("La operación es reversible: el botón Reactivar oficio lo devuelve a la lista."),
  p("Para consultar los oficios anulados, deberá marcarse la casilla Ver anulados del panel de búsqueda; se presentan atenuados y con el estado ANULADO. Un oficio anulado no admite cambios mientras no se reactive."),
  aviso("Utilidad práctica:", "al anular un oficio, su Referencia oficio queda liberada. De este modo puede retirarse un registro mal digitado y volver a darlo de alta correctamente."),

  h2("4.3 Crear usuarios"),
  ...pasos([
    "Abra la pestaña Usuarios.",
    "Complete el usuario, el nombre y la contraseña (por duplicado).",
    "Pulse Crear usuario.",
  ]),
  p("El botón Nuevo deja el formulario en blanco. Resulta de utilidad cuando se ha abierto una cuenta para editarla y se desea crear otra sin necesidad de guardar los cambios."),
  aviso("Alcance del administrador:", "únicamente puede crear cuentas con rol «usuario». La creación de administradores y superusuarios corresponde al superusuario."),

  h2("4.4 Editar, eliminar y restablecer contraseñas"),
  p("Seleccione a la persona en la lista de usuarios existentes y utilice el botón correspondiente:"),
  vinieta("Editar: modifica su nombre o su contraseña."),
  vinieta("Restablecer contraseña: se utiliza cuando la persona ha olvidado la suya; se abre una ventana donde se registra la nueva clave."),
  vinieta("Eliminar: da de baja la cuenta, previa confirmación."),
  espacio(120),
  p("El administrador únicamente alcanza a las cuentas con rol «usuario» y a la suya propia. No puede editar, eliminar ni restablecer la contraseña de otro administrador ni de un superusuario.",
    { juntar: true }),
  p("En la tabla, las filas indican quién actúa y las columnas a quién puede gestionar:",
    { italics: true, size: 20, color: AZUL_SUAVE, juntar: true }),
  tabla(
    ["Quién actúa", "Superusuario", "Administrador", "Usuario", "Su cuenta"],
    [
      ["Superusuario", "Sí", "Sí", "Sí", "Sí"],
      ["Administrador", "No", "No", "Sí", "Sí"],
    ],
    [2360, 1900, 1900, 1600, 1600],
  ),

  h2("4.5 Configuración: numeración de la Referencia UDC"),
  p("La Referencia UDC se numera de forma independiente para cada institución y se reinicia cada año (apartado 6.4). En la pestaña Configuración se registra, por única vez y por institución, la última referencia utilizada con anterioridad, a fin de que la aplicación continúe la numeración a partir de la siguiente."),
  ...pasos([
    "Seleccione la institución.",
    "Indique la última Referencia UDC utilizada, por ejemplo REQ-UDC-SB-2026-0240.",
    "Pulse Guardar.",
  ]),
  p("La pantalla muestra en todo momento cuál será la próxima Referencia UDC de la institución seleccionada. Esta misma pestaña indica la carpeta en la que la aplicación guarda la información, dato de utilidad cuando se trabaja sobre una carpeta compartida."),

  h2("4.6 Configuración: tipos de acción"),
  p("El tipo de acción identifica lo que el oficio solicita y se elige de un catálogo, de modo que todos los registros empleen la misma denominación. El catálogo se administra en la pestaña Configuración, apartado Tipos de acción, y contempla tres operaciones:"),
  vinieta("Agregar: incorpora un tipo nuevo. No se admiten duplicados."),
  vinieta("Renombrar: corrige la denominación y la actualiza en todos los oficios que la utilizaban."),
  vinieta("Eliminar: retira el tipo, siempre que ningún oficio lo esté utilizando."),
  p("La lista indica en cuántos oficios se emplea cada tipo."),
  aviso("Reservado a gestores:", "el mantenimiento del catálogo corresponde a los administradores y al superusuario."),

  h2("4.7 Carga masiva de oficios"),
  p("Permite dar de alta de una sola vez los oficios que se venían llevando en la matriz de Excel, sin necesidad de registrarlos uno por uno. Se encuentra en la pestaña Configuración."),
  ...pasos([
    "Pulse Cargar archivo, en el apartado Carga masiva de oficios.",
    "Seleccione la matriz (.xlsx) o un archivo CSV con la misma cabecera.",
    "Revise el resumen que se presenta antes de guardar.",
    "Pulse Importar para confirmar.",
  ]),
  aviso("El archivo debe respetar el formato establecido:", "la cabecera en la fila 4, de la columna B a la AA, con todas sus columnas y en su orden. La primera columna corresponde a la Institución del Estado. Si el formato no coincide, la aplicación rechaza el archivo e indica qué columna no corresponde."),
  espacio(160),
  p("Antes de guardar información alguna se presenta una vista previa con los oficios que se van a incorporar y los avisos pertinentes. Conviene tener en cuenta lo siguiente:"),
  vinieta("La Referencia UDC no se toma del archivo: la asigna la aplicación según la institución de cada fila."),
  vinieta("Las filas que comparten la misma Referencia oficio se agrupan en un solo oficio, y cada una de ellas aporta una persona investigada."),
  vinieta("Los responsables de la matriz se identifican por su nombre. Si no se localiza la cuenta, o si el nombre corresponde a más de una, el oficio se incorpora sin responsable y en estado Por asignar."),
  vinieta("Los oficios que se incorporan sin responsable pierden su fecha de respuesta, que deberá registrarse nuevamente al asignarlos."),
  vinieta("Los oficios importados no llevan el documento del oficio ni la respuesta en PDF; pueden adjuntarse posteriormente desde la pestaña Oficios."),
  vinieta("Los oficios ya registrados no se duplican: se omiten y se informa de ello."),

  saltoPagina(),
  h1("5. Rol Superusuario"),
  p("El superusuario dispone de la totalidad de las funciones anteriores y es el único autorizado para crear administradores y para gestionar las copias de seguridad. Corresponde a la primera cuenta creada en la aplicación."),

  h2("5.1 Crear administradores y superusuarios"),
  p("En la pestaña Usuarios, el desplegable de rol ofrece los tres roles disponibles, de modo que pueden crearse cuentas de superusuario, de administrador o de usuario."),
  aviso("Al crear un superusuario:", "la nueva cuenta tendrá su mismo alcance, incluida la facultad de gestionar la cuenta de quien la creó."),

  h2("5.2 Gestionar cualquier cuenta"),
  p("El superusuario puede editar, eliminar y restablecer la contraseña de cualquier cuenta, incluidas las de otros administradores y superusuarios."),
  p("De esta forma se resuelve el olvido de contraseña de un administrador y también el de un superusuario, cuya clave puede ser restablecida por otro superusuario."),
  aviso("Protección:", "el sistema no admite quedarse sin superusuarios. El último no puede eliminarse ni cambiar de rol; para ello deberá crearse previamente otro superusuario."),

  h2("5.3 Copias de seguridad"),
  p("La aplicación genera una copia diaria de forma automática, la primera vez que se abre en el día. Las copias se almacenan comprimidas en la subcarpeta respaldos y se conservan durante los últimos 30 días."),
  p("En la pestaña Configuración, el superusuario dispone de un panel exclusivo que indica la última copia realizada y el número de copias almacenadas, con dos opciones:"),
  vinieta("Crear copia ahora: genera una copia en el momento."),
  vinieta("Abrir carpeta de copias: accede a la ubicación en que se almacenan."),
  p("Las copias comprenden los oficios, las cuentas, la numeración, el catálogo de tipos de acción y la bitácora. No incluyen los documentos de los oficios ni las respuestas en PDF."),

  saltoPagina(),
  h1("6. Reglas del sistema"),
  p("Las reglas que se enuncian a continuación se aplican en todos los casos, con independencia del rol."),

  h2("6.1 Fechas"),
  vinieta("Ninguna fecha puede ser posterior al día actual; el calendario no admite fechas futuras."),
  vinieta("La fecha de oficio no puede ser posterior a la de recepción."),
  vinieta("La fecha de asignación no puede ser anterior a la de recepción."),
  vinieta("La fecha de respuesta no puede ser anterior a la de recepción."),
  vinieta("El registro de una fecha de respuesta finaliza el oficio."),

  h2("6.2 Estados y responsable"),
  tabla(
    ["Situación", "Estado resultante"],
    [
      ["Oficio sin responsable",
       { texto: "Por asignar (único estado posible)", color: POR_ASIGNAR, negrita: true }],
      ["Se designa un responsable",
       { texto: "Pasa automáticamente a En proceso", color: EN_PROCESO, negrita: true }],
      ["Se registra la fecha de respuesta",
       { texto: "Pasa a Finalizado", color: FINALIZADO, negrita: true }],
    ],
    [4200, 5160],
  ),
  espacio(200),
  p("Los estados En proceso y Finalizado requieren que el oficio cuente con responsable asignado."),
  p("En la pestaña Oficios cada estado se identifica con este mismo color.",
    { italics: true, size: 20, color: AZUL_SUAVE }),

  h2("6.3 Requisitos para finalizar"),
  p("Para marcar un oficio como Finalizado, el expediente debe encontrarse completo:"),
  vinieta("Fecha de asignación registrada."),
  vinieta("Fecha de respuesta registrada."),
  vinieta("Respuesta en PDF adjunta."),
  p("Si faltara alguno de los tres, la aplicación indica cuál. Tampoco podrá retirarse la respuesta de un oficio finalizado sin reabrirlo previamente, eliminando su fecha de respuesta."),

  h2("6.4 La Referencia UDC"),
  p("La Referencia UDC la genera la aplicación con el formato REQ-UDC-SIGLA-AÑO-SECUENCIAL, en el que la sigla corresponde a la institución que remite el oficio:"),
  tabla(
    ["Institución del Estado", "Referencia"],
    [
      ["Superintendencia de Bancos", "REQ-UDC-SB-2026-0001"],
      ["Fiscalía General del Estado", "REQ-UDC-FGE-2026-0001"],
    ],
    [4200, 5160],
  ),
  espacio(200),
  vinieta("Cada institución mantiene su propia numeración, independiente de la otra."),
  vinieta("El secuencial se reinicia en 0001 el primer día de cada año."),
  vinieta("La referencia no se digita, no se repite y no se reutiliza."),
  p("Por este motivo la Institución del Estado constituye un campo obligatorio del registro: de ella depende la nomenclatura de la referencia."),
  p("La Referencia oficio, en cambio, la registra el usuario y tampoco admite duplicados."),

  h2("6.5 Personas investigadas y cantidad"),
  vinieta("Un oficio puede comprender a varias personas, naturales o jurídicas."),
  vinieta("La cantidad de investigados no se digita: la aplicación la obtiene del detalle y la actualiza al incorporar o retirar a una persona."),
  vinieta("El detalle se registra en el propio formulario de alta y se modifica con doble clic sobre el oficio."),

  h2("6.6 Auditoría"),
  p("Toda operación que modifica información queda registrada con su fecha, su hora y la persona que la realizó: alta de oficios, cambios de estado, de responsable o de prioridad, incorporación y retiro de personas investigadas, correcciones, anulaciones, cargas masivas, documentos adjuntos, exportaciones, mantenimiento del catálogo de tipos de acción, altas y bajas de cuentas, cambios de contraseña e ingresos al sistema, incluidos los intentos fallidos."),

  saltoPagina(),
  h1("7. Preguntas frecuentes"),

  h3("No visualizo los oficios de mis compañeros"),
  p("Corresponde al rol Usuario, que accede únicamente a los oficios que ha registrado o que tiene asignados. Los administradores y el superusuario visualizan la totalidad."),

  h3("He olvidado mi contraseña"),
  p("Deberá solicitarse a un administrador o al superusuario que utilice la opción Restablecer contraseña. La nueva clave se registra en ese momento."),

  h3("No puedo registrar un oficio sin adjuntar el documento"),
  p("Es el comportamiento previsto: el documento del oficio, en PDF o Word, es obligatorio. Si posteriormente se advirtiera que se adjuntó el archivo equivocado, deberá utilizarse Cambiar oficio."),

  h3("No encuentro el campo Cantidad de investigados"),
  p("La cantidad no se digita. Se obtiene de las personas registradas en el bloque Personas investigadas del formulario, que también puede modificarse con doble clic sobre el oficio."),

  h3("El tipo de acción que necesito no figura en el desplegable"),
  p("El desplegable presenta el catálogo del área. Deberá solicitarse a un administrador o al superusuario que incorpore el tipo requerido desde la pestaña Configuración."),

  h3("No puedo marcar el oficio como Finalizado"),
  p("Finalizar exige fecha de asignación, fecha de respuesta y la respuesta en PDF adjunta. El mensaje indica cuál de los tres falta."),

  h3("He finalizado un oficio por error"),
  p("Deberá eliminarse su fecha de respuesta mediante el botón Limpiar del calendario y guardar nuevamente."),

  h3("Registré un oficio con un dato equivocado"),
  p("Si se trata del estado, el responsable, las fechas de asignación o respuesta, el tipo de acción, la prioridad o la observación, deberá corregirse en el panel de modificación. Si el error afecta a la Referencia oficio, la Causal o las fechas de oficio o recepción, deberá solicitarse a un administrador su corrección desde Mantenimiento."),

  h3("Registré un oficio duplicado"),
  p("Un administrador o el superusuario pueden anularlo desde Mantenimiento. El oficio se retira de la lista y de los indicadores, si bien se conserva; además, su Referencia oficio queda nuevamente disponible."),

  h3("La carga masiva rechaza mi archivo"),
  p("El archivo debe respetar el formato establecido, con la cabecera en la fila 4 y todas sus columnas en su orden, siendo la primera la Institución del Estado. El mensaje señala qué columna no corresponde."),

  h3("Aparece el mensaje «Otro usuario está guardando cambios en este momento»"),
  p("Dos personas han guardado de forma simultánea. Deberá esperarse unos segundos y repetir la operación; el mensaje evita que una modificación se sobreponga a la otra."),

  h3("Al pulsar Ver respuesta (PDF) se ofrece abrirlo con otro programa"),
  p("El visor integrado no se encuentra disponible en ese equipo. El documento puede consultarse con el lector de PDF del sistema."),

  h3("No aparece la opción para crear administradores"),
  p("Constituye una facultad exclusiva del superusuario. Si se requiriera una cuenta de administrador, deberá solicitarse."),

  espacio(400),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    border: { top: { style: BorderStyle.SINGLE, size: 4, color: BORDE_FUERTE, space: 10 } },
    spacing: { before: 200 },
    children: [new TextRun({
      text: "Banco del Pacífico · Unidad de Cumplimiento · Uso interno",
      size: 18, color: AZUL_SUAVE, font: "Calibri",
    })],
  }),
];

// ---------- ÍNDICE ----------
// Se construye después del contenido, cuando ENTRADAS ya tiene todos los
// títulos. Los números de página se leen de paginas.json, que genera la
// segunda pasada del script de compilación; si no existe, quedan en blanco.
let PAGINAS = {};
try {
  PAGINAS = JSON.parse(fs.readFileSync(__dirname + "/paginas.json", "utf8"));
} catch (e) {
  PAGINAS = {};
}

// Ancho útil de la página: 12240 - 1440 de margen a cada lado.
const ANCHO_UTIL = 9360;

const entradaIndice = ({ texto, nivel }) => {
  const tamano = nivel === 0 ? 22 : 21;
  const color = nivel === 0 ? AZUL : AZUL_SUAVE;
  const run = (opts) => new TextRun({
    bold: nivel === 0, size: tamano, color, font: "Calibri", ...opts,
  });
  return new Paragraph({
    spacing: { before: nivel === 0 ? 160 : 0, after: nivel === 0 ? 40 : 30, line: 264 },
    indent: { left: nivel === 0 ? 0 : 340 },
    tabStops: [{ type: TabStopType.RIGHT, position: ANCHO_UTIL, leader: LeaderType.DOT }],
    children: [
      run({ text: texto }),
      run({ children: [new Tab()], color: PUNTEADO }),
      run({ text: String(PAGINAS[texto] === undefined ? "" : PAGINAS[texto]) }),
    ],
  });
};

const indice = [
  new Paragraph({
    spacing: { before: 0, after: 260 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 10, color: AZUL, space: 8 } },
    children: [new TextRun({ text: "Índice", bold: true, size: 32, color: AZUL, font: "Calibri" })],
  }),
  ...ENTRADAS.map(entradaIndice),
  saltoPagina(),
];

// ---------- PIE DE PÁGINA ----------
const pieDePagina = new Footer({
  children: [new Paragraph({
    spacing: { before: 120 },
    border: { top: { style: BorderStyle.SINGLE, size: 4, color: BORDE, space: 8 } },
    tabStops: [{ type: TabStopType.RIGHT, position: ANCHO_UTIL }],
    children: [
      new TextRun({
        text: `Manual de usuario · Versión ${VERSION_DOCUMENTO} · ${FECHA_ELABORACION}`
              + `  |  Aplicación versión ${VERSION_APLICACION}`,
        size: 16, color: AZUL_SUAVE, font: "Calibri",
      }),
      new TextRun({ children: [new Tab()], size: 16, font: "Calibri" }),
      new TextRun({
        children: [PageNumber.CURRENT],
        bold: true, size: 18, color: AZUL, font: "Calibri",
      }),
    ],
  })],
});

// ---------- DOCUMENTO ----------
const doc = new Document({
  creator: "Unidad de Cumplimiento - Banco del Pacífico",
  title: "Manual de usuario - Control de Oficios",
  description: "Manual de usuario del sistema Control de Oficios",
  features: { updateFields: true },
  numbering: {
    config: [
      {
        reference: "vinetas",
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 520, hanging: 260 } } } },
          { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 900, hanging: 260 } } } },
        ],
      },
      {
        reference: "pasos",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 520, hanging: 260 } } } },
        ],
      },
    ],
  },
  sections: [
    {
      properties: {
        titlePage: true,   // la portada no lleva número de página
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1300, right: 1440, bottom: 1300, left: 1440 },
        },
      },
      footers: {
        default: pieDePagina,
        first: new Footer({ children: [new Paragraph({ children: [] })] }),
      },
      children: [...portada, ...indice, ...contenido],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("/home/user/ControlOficios/Manual de usuario - Control de Oficios.docx", buffer);
  console.log("Manual generado");
});
