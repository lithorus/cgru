#pragma once

#include "../libafanasy/name_af.h"
#include "../libafanasy/blockdata.h"

#include "item.h"
#include "blockinfo.h"

class ListTasks;

class ItemJobBlock : public Item
{
public:
   ItemJobBlock( const af::BlockData* block, ListTasks * list);
   ~ItemJobBlock();

   virtual QSize sizeHint( const QStyleOptionViewItem &option) const;

   void update( const af::BlockData* block, int type);

   inline int getNumBlock() const { return numblock; }

   virtual inline const QVariant getToolTip()      const { return tooltip;      }

   uint32_t state;
   QString  blockName;
   QString  dependmask;
   QString  tasksdependmask;
   QString  command;
   int      capacity;
   QString  workingdir;
   QString  files;
   QString  cmdpre;
   QString  environment;
   QString  cmdpost;
   QString  taskstype;
   QString  tasksname;
   QString  parsertype;
   QString  hostsmask;
   QString  hostsmask_exclude;
   int      maxhosts;
   QString  maxhosts_str;
   int      need_memory;
   int      need_hdd;
   int      need_power;
   QString  need_properties;
   bool     varcapacity;
   bool     multihost;
   bool     multuhost_samemaster;
   QString  multihost_service;

   int      errors_retries;
   int      errors_avoidhost;
   int      errors_samehost;
   uint32_t tasksmaxruntime;

   bool numeric;    ///< Whether the block is numeric.
   int  first;      ///< First tasks frame.
   int  last;       ///< Last tasks frame.
   int  pertask;    ///< Tasks frames per task.
   int  inc;        ///< Tasks frames increment.

   QString description;

   static const int ItemId = 1;

   bool tasksHidded;

   inline void generateMenu( int id_block, QMenu * menu, QWidget * qwidget) { info.generateMenu( id_block, menu, qwidget);}

   inline void blockAction( int id_block, int id_action, ListItems * listitems) { info.blockAction( id_block, id_action, listitems);}

   bool mousePressed( const QPoint & pos,const QRect & rect);

   enum SortType
   {
      SNULL = 0,
      SStarts,
      SErrors,
      SHost,
      STime,
      SState
   };

   inline int  getSortType()     const { return sort_type;     }
   inline bool isSortAsceding()  const { return sort_ascending;}

   /// Return old sorting type:
   inline int resetSortingParameters() { int value = sort_type; sort_type = 0; sort_ascending = false; return value;}

protected:
   virtual void paint( QPainter *painter, const QStyleOptionViewItem &option) const;

private:
   void generateToolTip();
   void updateToolTip();

private:
   static const int HeightHeader;
   static const int HeightFooter;

private:
   QString tooltip;

   int height;
   int width;

   int numblock;
   QString  blockToolTip;

   BlockInfo info;

   static const int WHost = 50;
   static const int WStarts = 60;
   static const int WErrors = 60;
   static const int WTime = 50;

   bool sort_ascending;
   int sort_type;

   ListTasks * listtasks;
};
